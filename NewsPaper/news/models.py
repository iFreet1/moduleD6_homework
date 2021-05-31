from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def __str__(self):
        return str(self.user.username)

    def UpdateRating(self):
        author = Author.objects.get(user=self.user)
        author_posts = Post.objects.filter(author=author, post_type="AR")
        author_comments_rating = Comment.objects.filter(user=self.user).values("rating")
        comment_author_posts_rating = Comment.objects.filter(post__in=author_posts).values("rating")

        sum_articles_rating = 0
        sum_comments_rating = 0
        sum_comments_author_posts_rating = 0

        for article in author_posts:
            sum_articles_rating += article.rating * 3

        for comment in author_comments_rating:
            sum_comments_rating += comment['rating']

        for comment in comment_author_posts_rating:
            sum_comments_author_posts_rating += comment['rating']

        self.rating = sum_articles_rating + sum_comments_rating + sum_comments_author_posts_rating
        self.save()

        # Для проверки работоспособности, возвращаем рейтинг
        return self.rating


class Category(models.Model):
    name = models.CharField(max_length=15, unique=True)
    subscribers = models.ManyToManyField(User, through="CategoryUser")

    def __str__(self):
        return str(self.name)


class CategoryUser(models.Model):
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PostCategory(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)


class Post(models.Model):
    article = 'AR'
    news = 'NW'

    POST_TYPES = [
        (article, 'Статья'),
        (news, 'Новость'),
    ]

    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=article)
    create_date = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField("Category", through="PostCategory")
    header = models.CharField(max_length=30)
    text = models.TextField()
    rating = models.IntegerField()

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:123]}...'

    def __str__(self):
        return self.header

    def get_absolute_url(self):  # добавим абсолютный путь чтобы после создания нас перебрасывало на страницу с товаром
        return f'/news/{self.id}'


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()