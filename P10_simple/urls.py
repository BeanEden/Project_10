"""P10_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from softdesk.views import ProjectViewSet, IssueViewSet, CommentViewSet, \
    ContributorViewSet, MyObtainTokenPairView, RegisterView

# Multiple routers are used to manage the nested ViewSets

router_projects = routers.DefaultRouter()
router_projects.register('projects', ProjectViewSet, basename='project')

router_issues = routers.DefaultRouter()
router_issues.register('issues', IssueViewSet, basename='issue')
router_issues.register('users', ContributorViewSet, basename='user')

router_comments = routers.DefaultRouter()
router_comments.register('comments', CommentViewSet, basename='comment')
router_comments.register('users', ContributorViewSet, basename='user')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('', include(router_projects.urls)),
    path('projects/<int:project_id>/', include(router_issues.urls)),
    path('projects/<int:project_id>/issues/<int:issue_id>/',
         include(router_comments.urls)),
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', RegisterView.as_view(), name='signup')
]
