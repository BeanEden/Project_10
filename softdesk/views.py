from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import MyTokenObtainPairSerializer, RegisterSerializer

from softdesk.models import Project, Issue, Comment, Contributor
from softdesk.serializers import ProjectListSerializer, ProjectDetailSerializer,\
    IssueListSerializer, IssueDetailSerializer,\
    CommentListSerializer, CommentDetailSerializer, \
    ContributorListSerializer, ContributorDetailSerializer

from softdesk.permissions import IsAllowedOrReadOnly

User = get_user_model()


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class MyObtainTokenPairView(TokenObtainPairView):

    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ProjectViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        wanted_items = set()
        for item in Contributor.objects.filter(user_assigned=user):
            project_id = item.project_associated_id
            wanted_items.add(item.pk)
        queryset = Project.objects.filter(pk__in=wanted_items)
        return queryset


class IssueViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        path = self.request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        queryset = Issue.objects.filter(project_associated = project)
        return queryset


class CommentViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        path = self.request.path_info
        split_path = path.split('/')
        issue_id = split_path[4]
        issue = Issue.objects.get(id=issue_id)
        queryset = Comment.objects.filter(issue_associated = issue)
        return queryset


class ContributorViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorListSerializer
    detail_serializer_class = ContributorDetailSerializer
    queryset = Contributor.objects.all()
    permission_classes = [IsAuthenticated, IsAllowedOrReadOnly]

    def get_queryset(self):
        path = self.request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        queryset = Contributor.objects.filter(project_associated = project)
        return queryset