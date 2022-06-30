from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models, transaction
from requests import request
from django.core.validators import ValidationError, validate_slug, slug_re
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

# PROJECT_TYPE = ['back-end', 'front-end', 'iOS', 'Android']

PROJECT_TYPE = [('back-end','back-end'),
                ('front-end','front-end'),
                ('iOS', 'iOS'),
                ('Android','Android')]

ISSUE_PRIORITY = [
    ('low', 'FAIBLE'),
    ('medium', 'MOYENNE'),
    ('high', 'ELEVEE')
]

ISSUE_TAG = [
    ('bug', 'BUG'),
    ('improvement', 'AMELIORATION'),
    ('task', 'TACHE')
]

ISSUE_STATUS = [
    ('to do', 'A faire'),
    ('ongoing', 'En cours'),
    ('done', 'Terminé')
]

PROJECT_PERMISSIONS = [
    ('modify', 'modifier'),
    ('read-only', 'lecture seule')
]

def clean_string(string, *args):
    string = string.casefold()
    for i in args:
        string = string.replace(i, "")
    return string


class User(AbstractUser):
    # contributions = models.ForeignKey(
    #     to='softdesk.Contributor', on_delete=models.CASCADE,
    #     related_name='users_on_project', null=True)
    # projects_contributed = models.ManyToManyField(
    #     'self',
    #     symmetrical=False,
    #     through="softdesk.Contributor"
    # )
    username = models.CharField(max_length=255, validators = [validate_slug], unique=True)
    first_name = models.CharField(max_length=255, validators = [validate_slug])
    last_name = models.CharField(max_length=255, validators = [validate_slug])
    email = models.EmailField(blank=False,unique=True)
    password = models.CharField(max_length=255, blank=False,
                                     validators=[validate_password])

    def __str__(self):
        return self.username

def set_username(instance, **kwargs):
    if not instance.username:
        clean_first_name = clean_string(instance.first_name, " ", "-")
        clean_last_name = clean_string(instance.last_name, " ", "-")
        username = clean_first_name + "-" + clean_last_name
        counter = 1
        while User.objects.filter(username=username):
            username = username + str(counter)
            counter += 1
        instance.username = username

models.signals.pre_save.connect(set_username, sender=User)


class Contributor(models.Model):
    role = models.CharField(max_length=255, validators = [validate_slug])
    project_associated = models.ForeignKey(to='softdesk.Project', on_delete=models.CASCADE, related_name='contributors', null = True)
    users_assigned = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='contributions', null=True)
    permission = models.CharField(max_length=255, choices=PROJECT_PERMISSIONS, blank=False,
                            default='read-only', validators = [validate_slug])


class Project(models.Model):
    title = models.CharField(max_length=255, blank=False, default='undefined', validators = [validate_slug])
    type = models.CharField(max_length=255, choices=PROJECT_TYPE, blank=False,
                            default='undefined', validators = [validate_slug])
    # author = models.CharField(max_length=255, default= 'nope')
    description = models.CharField(max_length=500, blank=True, validators = [validate_slug])
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='projects_created', null=True)
    users_on = models.ForeignKey(
        to='softdesk.Contributor', on_delete=models.CASCADE,
        related_name='projects_assigned', null=True)

    def __str__(self):
        return self.title


class Issue(models.Model):
    title = models.CharField(max_length=255, blank=False, default='undefined')
    tag = models.CharField(max_length=255, choices=ISSUE_TAG, blank=False,
                           default='undefined')
    priority = models.CharField(max_length=255, choices=ISSUE_PRIORITY,
                                blank=False, default='undefined')
    status = models.CharField(max_length=255, choices=ISSUE_STATUS, blank = False)
    # author = models.CharField(max_length=255, default= 'nope')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='issues_created', null=True)
    description = models.CharField(max_length=500, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_time = models.DateTimeField(auto_now=True)
    project_associated = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name='issues', null = True)
    assignee = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, related_name='issues_assigned', null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    issue_associated = models.ForeignKey(to=Issue, on_delete=models.CASCADE, related_name='comments', null = True)
    # author = models.CharField(max_length=255, default= 'nope')
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='comments_created', null=True)
    description = models.CharField(max_length=500, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description



    # def validate_project_data(self):
    #     invalid_values = []
    #     value = [self.title, self.description]
    #     for val in value:
    #         try:
    #             validate_slug(val)
    #         except ValidationError:
    #             invalid_values.append(val)
    #
    #     if invalid_values:
    #         raise ValidationError(
    #             self.error_message['invalid characters'] % invalid_values)

    # def validate_type(self):