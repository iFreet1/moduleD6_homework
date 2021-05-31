from django.shortcuts import render, reverse, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.core.mail import send_mail, EmailMultiAlternatives # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string # импортируем функцию, которая срендерит наш html в текст
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import datetime
from .models import Post, Category, PostCategory, CategoryUser
from .filters import NewsFilter
from .forms import PostForm
from django.core.paginator import Paginator


class NewsList(ListView):
    model = Post
    template_name = "news.html"
    context_object_name = "news"
    queryset = Post.objects.order_by('-create_date')
    paginate_by = 10
    form_class = PostForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        context['form'] = PostForm()
        return context


class SearchList(ListView):
    model = Post
    template_name = "search.html"
    context_object_name = "news"
    queryset = Post.objects.order_by('-create_date')
    paginate_by = 10
    form_class = PostForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

        return super().get(request, *args, **kwargs)


class NewsDetail(DetailView):
    model = Post
    template_name = "article.html"
    context_object_name = "article"
    queryset = Post.objects.all()


class PostDetailView(DetailView):
    template_name = 'news_detail.html'
    queryset = Post.objects.all()


class NewsCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'news_create.html'
    form_class = PostForm
    permission_required = ('news.add_post',)

    def post(self, request, *args, **kwargs):
        posts_today = Post.objects.filter(create_date__gt=timezone.now().date(), author__user=request.user)

        # проверяем, не запостил ли данный пользователь более трех постов за сегодня
        if (len(posts_today) >= 3):
            print('На сегодня лимит постов исчерпан!')
            return super().get(request, *args, **kwargs)

        form = self.form_class(request.POST)

        post = Post(
            header=request.POST['header'],
            text=request.POST['text'][:50],
        )

        if form.is_valid():
            form.save()

            post_obj = Post.objects.get(header=request.POST['header'])

            # отправка email подписантам
            # получем наш html
            html_content = render_to_string(
                'news_announce.html',
                {
                    'article': post,
                    'user': request.user,
                    'news_link': f'http://127.0.0.1:8000/news/{post_obj.id}'
                }
            )

            categorys = post_obj.category.filter()
            subscribers = []
            print('222', categorys)
            for category in categorys:
                for user in category.subscribers.filter().distinct():
                    subscribers.append(user)

            # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
            for user in subscribers:
                msg = EmailMultiAlternatives(
                    subject=f'{post.header}',
                    body=post.text,  # это то же, что и message
                    from_email='xxxx@gmail.com',
                    to=[user.email],  # это то же, что и recipients_list
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html

                msg.send()  # отсылаем
                print('Отправили', user.email)

        # отправляем письмо
        # send_mail(
        #     subject=f'{post.header} ', # {post.create_date.strftime("%Y-%M-%d")}
        #     # имя клиента и дата записи будут в теме для удобства
        #     message=post.text,  # сообщение с кратким описанием проблемы
        #     from_email='ifreet4@gmail.com',
        #     # здесь указываете почту, с которой будете отправлять (об этом попозже)
        #     recipient_list=['ifreet1@ya.ru']  # здесь список получателей. Например, секретарь, сам врач и т. д.
        # )

        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'news_create.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class NewsDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'news_delete.html'
    context_object_name = "article"
    success_url = '/news/'
    permission_required = ('news.delete_post',)

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


def SybscribeUser(request, pk):
    user = request.user
    post = Post.objects.get(id=pk)
    categorys = post.category.filter()


    for category in categorys:
        subscribers = CategoryUser.objects.filter(user=user, category=category)  #category.subscribers.filter(CategoryUser__user=user)

        # Есди нет подписок на данную категорию, подписываемся
        if len(subscribers) == 0:
            category.subscribers.set([user])
            category.save()
            print("Нет подписок")

    return redirect(f'/news/{pk}')
