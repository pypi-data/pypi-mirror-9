from .models import Access, Consumer

def get_or_create_consumer(request):
    if request.user.is_authenticated():
        return get_or_create_authenticated_consumer( request )
    return get_or_create_anonymous_consumer( request )
    
def get_or_create_access(request, scope):
    consumer = get_or_create_consumer( request )
    access, created = Access.objects.get_or_create(consumer=consumer, scope=scope)
    return access
    
def get_or_create_anonymous_consumer(request):
    consumer, created = Consumer.objects.get_or_create(ip=request.META['REMOTE_ADDR'])
    return consumer
    
def get_or_create_anonymous_access(request, scope):
    consumer = get_or_create_anonymous_consumer( request )
    access, created = Access.objects.get_or_create(consumer=consumer, scope=scope)
    return access
    
def get_or_create_authenticated_consumer(request):
    consumer, created = Consumer.objects.get_or_create(user=request.user)
    return consumer
    
def get_or_create_authenticated_access(request, scope):
    consumer = get_or_create_authenticated_consumer( request )
    access, created = Access.objects.get_or_create(consumer=consumer, scope=scope)
    return access
