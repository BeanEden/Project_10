from django.contrib.auth.models import User
from django.conf import settings
from django.db import models, transaction
from requests import request

class User(models.Model):
    # projects = models.ManyToManyField(
    #     'self',
    #     symmetrical=False,
    #     through="softdesk.Contributors"
    # )
    # user_intel = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    name = models.CharField(max_length=255)
# class Contributors(models.Model):
#     subscriptions = models.ManyToManyField(
#         'self',
#         symmetrical=False,
#         through="softdesk.Contributors"
#     )
#     project_contributed = models.ForeignKey(
#         to='softdesk.Project', on_delete=models.CASCADE,
#         related_name='projects_contributed')
    projects_on = models.ForeignKey(
        to='softdesk.Project', on_delete=models.CASCADE,
        related_name='users_on_project')


# class Contributors(models.Model):
#     user_contributing = models.ForeignKey(
#         to='softdesk.User', on_delete=models.CASCADE,
#         related_name='users_contributing')
#     project_contributed = models.ForeignKey(
#         to='softdesk.Project', on_delete=models.CASCADE,
#         related_name='projects_contributed')
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)


class Project(models.Model):
    name = models.CharField(max_length=255)
    # users = models.ManyToManyField('self',
    #     symmetrical=False,
    #     through="softdesk.Contributors"

    # user_contributing = models.ForeignKey(
    #     to='softdesk.User', on_delete=models.CASCADE,
    #     related_name='users_contributing')


class Issue(models.Model):
    name = models.CharField(max_length=255)
    project_associated = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name='issues')


class Comment(models.Model):
    name = models.CharField(max_length=255)
    issue_associated = models.ForeignKey(to=Issue, on_delete=models.CASCADE, related_name='comments')