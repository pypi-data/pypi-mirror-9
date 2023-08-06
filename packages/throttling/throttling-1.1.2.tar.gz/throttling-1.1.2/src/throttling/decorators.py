#!/usr/bin/env python
# encoding: utf-8
from django.http              import HttpResponse
from django.conf              import settings
from django.db.models         import Count
from django.utils             import timezone
from django.core.urlresolvers import resolve
from userroles import roles
from .consts import THROTTLING_CONFIG, THROTTLING_STATUS_CODE
from .consts import THROTTLING_INTERVAL, THROTTLING_NUMBER_OF_REQUESTS
from .utils  import get_or_create_anonymous_access, get_or_create_authenticated_access, get_or_create_access
from .models import Access
from datetime  import timedelta
from functools import wraps
    

def throttle(*args, **kwargs):
    
    config = kwargs.get('config', None)

    if THROTTLING_CONFIG and config:
        # set values to throttle args according to pre-defined options
        for key,value in THROTTLING_CONFIG.get( config, {} ).iteritems():
            kwargs[ key ] = value
    
    if args:
        number_of_requests = args[0] 
    else:
        number_of_requests = kwargs.get('number_of_requests', THROTTLING_NUMBER_OF_REQUESTS)
    all_with_role = kwargs.get('all_with_role', None)
    per_anonymous = kwargs.get('per_anonymous', False)
    all_anonymous = kwargs.get('all_anonymous', None)
    all_users     = kwargs.get('all_users', False)
    role          = kwargs.get('role', None)
    group         = kwargs.get('group', None)
    all_in_group  = kwargs.get('all_in_group', None)
    scope         = kwargs.get('scope', None)
    interval      = kwargs.get('interval', THROTTLING_INTERVAL)
    
    if isinstance(role, basestring):
        role = roles.get( role )
                                
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not scope:
                # set default value to scope
                url_name = resolve( request.path ).url_name
                throttle_scope = "%s::%s" % (request.method, url_name)
            else:
                throttle_scope = scope

            if per_anonymous:
                if user.is_authenticated():
                    # Proceed if user is authenticated
                    return f(request, *args, **kwargs)
                else:
                    # Throttle each anonymous user
                    access = get_or_create_anonymous_access( request, throttle_scope )
                    current_request_count = access.count_requests()
            
            elif all_anonymous:
                if user.is_authenticated():
                    # Proceed if user is authenticated
                    return f(request, *args, **kwargs)
                else:
                    # All anonymous users share the same 'pool' of allowed request
                    access = get_or_create_anonymous_access( request, throttle_scope )
                    current_request_count = Access.objects.filter(scope=throttle_scope).anonymous().count_requests()
            
            elif group or all_in_group:
                group_name = group or all_in_group
                if user.is_authenticated() and user.groups.filter(name=group_name).exists():
                    access = get_or_create_authenticated_access( request, throttle_scope )
                    if group:
                        # Throttle if user belongs to Group
                        current_request_count = access.count_requests()
                    else:
                        # All users within a Group share the same 'pool' of allowed request
                        pool_access = Access.objects.filter(consumer__user__groups__name=group_name, scope=throttle_scope)
                        current_request_count = pool_access.count_requests()
                else:
                    # Proceed if user is not authenticated
                    return f(request, *args, **kwargs)
            
            elif all_with_role:
                pass
            
            elif role:
                if not user.is_authenticated() or not hasattr(user, 'role'):
                    # Fails to proceed if user not authenticated or has no role
                    return HttpResponse(status=THROTTLING_STATUS_CODE)
                elif user.role == role or roles.get( user.role.name ).subrole_of( role ):
                    # Throttle each user with equal or lower role
                    access = get_or_create_authenticated_access( request, throttle_scope )
                    current_request_count = access.count_requests()
                else:
                    # Proceed if user role is hierarchically above given role
                    return f(request, *args, **kwargs)
            
            elif all_users:
                # All users (authenticated and anonymous) share the same 'pool' of allowed request
                access = get_or_create_access( request, throttle_scope )
                current_request_count = Access.objects.filter(scope=throttle_scope).count_requests()
            
            else:
                # Throttle each user (authenticated and anonymous)
                access = get_or_create_access( request, throttle_scope )
                current_request_count = access.count_requests()
  
            expiration_date = access.min_datemark() + timedelta(minutes=interval)
                
            if number_of_requests > current_request_count:
                if not hasattr(request, 'access_updated'):
                    # Do this only once per request
                    request.access_updated = True
                    if expiration_date < timezone.now():
                        # reset count if exceeded the time interval since datemark
                        access.reset_count()
                    else:
                        # increment request count
                        access.increment_count()
                # Proceed if under the allowed number of request
                return f(request, *args, **kwargs)
                
            elif expiration_date < timezone.now():
                if not hasattr(request, 'access_updated'):
                    # Do this only once per request
                    request.access_updated = True
                    # reset count if exceeded the time interval since datemark
                    access.reset_count()
                return f(request, *args, **kwargs)
                
            return HttpResponse(status=THROTTLING_STATUS_CODE)
        
        return wrapper	
    return decorator
