from django_filters import rest_framework as filters

from .models import Amounttake


class AmounttakeFilter(filters.FilterSet):

    CHOICES = (
        ('ascending','Возрастание'),
        ('descending','Убывание'),

    )
    CHOICES2 = (
        ('sort_by_date+','Новые поступления'),
        ('sort_by_date-','Старые поступления')
    )

    ordering = filters.ChoiceFilter(label='Сортировка по сумме',choices=CHOICES,
                                           method='filter_by_order')

    date_ordering = filters.ChoiceFilter(label='Сортировка по дате', choices=CHOICES2,
                                                method='filter_by_date')

    class Meta:
        model = Amounttake
        fields = {
            'amount': ['icontains'],
            'amount_date': ['icontains'],
        }
        exclude = ('amount', 'amount_date',)

    def filter_by_order(self, queryset, name, value):
        expression = '-amount' if value == 'ascending' else 'amount'
        return queryset.order_by(expression)

    def filter_by_date(self, queryset, name, value):
        expression = '-amount_date' if value == 'sort_by_date+' else 'amount_date'
        return queryset.order_by(expression)