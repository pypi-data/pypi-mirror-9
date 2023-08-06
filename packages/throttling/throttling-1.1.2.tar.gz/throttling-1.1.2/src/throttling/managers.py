#!/usr/bin/env python
# encoding: utf-8
from django.db.models import F, Count, Min, Sum, query
from .consts import COUNT_VALUE_AFTER_RESET
from django.utils import timezone


class AccessQuerySet(query.QuerySet):
    
    def anonymous(self):
        return self.filter(consumer__ip__isnull=False)
        
    def count_requests(self):
        return self.aggregate(count=Sum('count'))['count']
        
    def min_datemark(self):
        return self.aggregate(min_date=Min('datemark'))['min_date']
