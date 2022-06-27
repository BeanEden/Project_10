from django.contrib.auth.models import User
from django.conf import settings
from django.db import models, transaction
from requests import request

class Users(User):
    name = models.CharField(max_length=255)
    contributions = models.ForeignKey(
        to='softdesk.Contributor', on_delete=models.CASCADE,
        related_name='users_on_project')


class Contributor(models.Model):
    role = models.CharField(max_length=255)


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # users_on = models.ForeignKey(
    #     to='softdesk.Contributor', on_delete=models.CASCADE,
    #     related_name='project_contributed', default=1)
    author = models.CharField(max_length=255, default= 'nope')


class Issue(models.Model):
    name = models.CharField(max_length=255)
    project_associated = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name='issues', null = True)
    author = models.CharField(max_length=255, default= 'nope')

class Comment(models.Model):
    name = models.CharField(max_length=255)
    issue_associated = models.ForeignKey(to=Issue, on_delete=models.CASCADE, related_name='comments', null = True)