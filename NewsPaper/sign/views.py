from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
# from NewsPaper.news.models import Author


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')

    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
        # author = Author(user=user, rating=0)
        # author.save()

    return redirect('/')