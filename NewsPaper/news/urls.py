from django.urls import path
from .views import NewsList, SearchList, NewsDetail, PostDetailView, NewsCreateView, NewsUpdateView, NewsDeleteView, SybscribeUser

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetail.as_view(), name='news_detail'),
    path('search', SearchList.as_view()),
    path('add', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete', NewsDeleteView.as_view(), name='news_delete'),
    path('<int:pk>/subscribe/', SybscribeUser, name='subscribe'),
]