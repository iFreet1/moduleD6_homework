import logging
import datetime

from django.conf import settings
from ...models import Post, CategoryUser, User

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    users = User.objects.all()

    today = datetime.date.today()
    monday_date = today - datetime.timedelta(days=today.weekday())

    for user in users:
        weak_posts = []
        categorys = CategoryUser.objects.filter(user=user)

        # категории на которые подписан пользователь
        for category in categorys:
            for post in Post.objects.filter(create_date__gt=monday_date, category=category):
                weak_posts.append(post)

        # отправка email подписантам
        # получем наш html
        html_content = render_to_string(
            'news_weak_announce.html',
            {
                'article': 'Все новости и посты за последнюю неделю',
                'user': user,
                'news_links': weak_posts
            }
        )

        msg = EmailMultiAlternatives(
            subject='Все новости и посты за последнюю неделю',
            body='',  # это то же, что и message
            from_email='xxxxxx@gmail.com',
            to=[user.email],  # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html

        msg.send()  # отсылаем


# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10"),
            # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")