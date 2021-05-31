from django_filters import FilterSet
from .models import Post


class NewsFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'create_date': ['gt'],
            'header': ['contains'],
            'author__user__username': ['contains'],
        }