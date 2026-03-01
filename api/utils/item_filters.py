import django_filters
from django.db.models import Q 
from api.models import Item

class ItemFilter(django_filters.FilterSet):
    item_type = django_filters.NumberFilter(field_name='item_type')
    category = django_filters.NumberFilter(field_name='category__id')
    location = django_filters.NumberFilter(field_name='location__id')
    lost_at_after = django_filters.DateFilter(field_name='lost_at', lookup_expr='gte')
    lost_at_before = django_filters.DateFilter(field_name='lost_at', lookup_expr='lte')
    found_at_after = django_filters.DateFilter(field_name='found_at', lookup_expr='gte')
    found_at_before = django_filters.DateFilter(field_name='found_at', lookup_expr='lte')

    queryset = django_filters.CharFilter(method='keyword_search', label='Keyword Search')

    class Meta:
        model = Item
        fields = ['item_type', 'category', 'location']

    def keyword_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )