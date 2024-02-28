from .models import Transaction
from django_filters import FilterSet, NumberFilter
class TransactionFilter(FilterSet):
    month = NumberFilter(field_name='created_at__month', label="month in number format")
    
    class Meta:
        model = Transaction
        fields = ['month', 'category']