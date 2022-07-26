from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from softdesk.models import Project, Issue, Comment, Contributor
from softdesk.serializers import ProjectListSerializer, \
    ProjectDetailSerializer,\
    IssueListSerializer, IssueDetailSerializer,\
    CommentListSerializer, CommentDetailSerializer, \
    ContributorListSerializer, ContributorDetailSerializer,\
    MyTokenObtainPairSerializer, RegisterSerializer
from softdesk.permissions import IsAllowedOrReadOnly

User = get_user_model()

# This file manages views (read operations) through viewSets
# Each viewSet has permission and serializer/detail_serializer classes
# List querySets are managed through "get_queryset" functions
# Create, update, delete operations are managed in serializers.py


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class \
                is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class MyObtainTokenPairView(TokenObtainPairView):
    """ Login View"""
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """ Sign up View"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ProjectViewSet(MultipleSerializerMixin, ModelViewSet):
    """ Project list and detail view"""
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        """get all projects related to the user (author or assigned)"""
        user = self.request.user
        wanted_items = set()
        for item in Contributor.objects.filter(user_assigned=user):
            wanted_items.add(item.pk)
        queryset = Project.objects.filter(pk__in=wanted_items)
        return queryset


class IssueViewSet(MultipleSerializerMixin, ModelViewSet):
    """ Issue list and detail view"""
    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        """get all issues related to project"""
        path = self.request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        queryset = Issue.objects.filter(project_associated=project)
        return queryset


class CommentViewSet(MultipleSerializerMixin, ModelViewSet):
    """ Comment list and detail view"""
    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        """get all comments related to the issue"""
        path = self.request.path_info
        split_path = path.split('/')
        issue_id = split_path[4]
        issue = Issue.objects.get(id=issue_id)
        queryset = Comment.objects.filter(issue_associated=issue)
        return queryset


class ContributorViewSet(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorListSerializer
    detail_serializer_class = ContributorDetailSerializer
    queryset = Contributor.objects.all()
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        """get all user assignments related to the project"""
        path = self.request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        queryset = Contributor.objects.filter(project_associated=project)
        return queryset
