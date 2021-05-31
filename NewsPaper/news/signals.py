from django.db.models.signals import post_save
from django.dispatch import receiver # импортируем нужный декоратор
from django.core.mail import mail_managers
from django.template.loader import render_to_string # импортируем функцию, которая срендерит наш html в текст
from django.core.mail import send_mail, EmailMultiAlternatives # импортируем класс для создание объекта письма с html
from .models import Post, PostCategory, Category, CategoryUser, User


# дублирование того что есть в views, в классе NewsCreateView, на всякий случай оставил и то, и то
@receiver(post_save, sender=Post)
def notify_managers_post(sender, instance, created, **kwargs):
    post = Post(
        header=instance.header,
        text=instance.text[:50],
    )

    # получем наш html
    html_content = render_to_string(
        'news_announce.html',
        {
            'article': post,
            'user': instance.author
        }
    )

    post_obj = Post.objects.get(header=instance.header)
    categorys = post_obj.category.filter()
    # categorys = PostCategory.objects.filter(post=instance)
    subscribers = []

    for category in categorys:
        print(category)
        for user in category.subscribers.filter().distinct():
            subscribers.append(user)

    # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
    for user in subscribers:
        msg = EmailMultiAlternatives(
            subject=f'{post.header}',
            body=post.text,  # это то же, что и message
            from_email='xxxxx@gmail.com',
            to=[user.email],  # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html

        msg.send()  # отсылаем
        print('Отправили', user.email)

    # if created:
    #     subject = f'{instance.author} {instance.create_date.strftime("%d %m %Y")}'
    # else:
    #     subject = f'Post changed for {instance.author} {instance.create_date.strftime("%d %m %Y")}'
    #
    # mail_managers(
    #     subject=subject,
    #     message=instance.text,
    # )