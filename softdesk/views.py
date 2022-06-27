from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from softdesk.models import Project, Issue, Comment, Contributor, User
from softdesk.serializers import ProjectListSerializer, ProjectDetailSerializer,\
    IssueListSerializer, IssueDetailSerializer,\
    CommentListSerializer, CommentDetailSerializer, \
    UserListSerializer, UserDetailSerializer,\
    ContributorListSerializer, ContributorDetailSerializer
from .serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
# from authentication.models import Users
from .serializers import RegisterSerializer
from rest_framework import generics
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
# from django.contrib.auth.models import User

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
    # queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.filter(author = self.request.user)
        return queryset


class IssueViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        path = self.request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        queryset = Issue.objects.filter(project_associated = project)
        return queryset


class CommentViewset(ReadOnlyModelViewSet):

    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        path = self.request.path_info
        split_path = path.split('/')
        issue_id = split_path[4]
        issue = Issue.objects.get(id=issue_id)
        queryset = Comment.objects.filter(issue_associated = issue)
        return queryset


class UserViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = UserListSerializer
    detail_serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class ContributorViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorListSerializer
    detail_serializer_class = ContributorDetailSerializer
    queryset = Contributor.objects.all()
    permission_classes = IsAuthenticated