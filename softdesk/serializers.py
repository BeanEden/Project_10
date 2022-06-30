from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from softdesk.models import Project, Issue, Comment, Contributor, set_username

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_slug

from django.contrib.auth import get_user_model
User = get_user_model()


class UserListSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class ContributorListSerializer(ModelSerializer):

    class Meta:
        model = Contributor
        fields = ['id','user_assigned', 'role',  'permission']

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        path = request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        username = request.data['user_assigned']
        project = Project.objects.get(id=project_id)
        user = User.objects.get(id=username)
        contributor = Contributor.objects.create(
            role = validated_data['role'],
            project_associated = project,
            user_assigned = user,
            author=user,
            permission = validated_data['permission']
        )
        # contributor.user_to_assign=user
        contributor.save()
        return contributor


class ProjectListSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'title', 'type', 'contributors', 'description']

        extra_kwargs = {
            'title': {'required': True},
            'type': {'required': True},
            'description': {'write_only': True}
        }

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        project = Project.objects.create(
            title= request.data['title'],
            type=request.data['type'],
            author=user,
            description=request.data['description'],
        )
        contributor = Contributor.objects.create(
            role = 'author',
            project_associated=project,
            user_assigned = user,
            author=user,
            permission = 'modify'
        )
        print(contributor)
        contributor.save()
        return project


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'title', 'tag', 'priority', 'status', 'author', 'description', 'assignee']

        extra_kwargs = {
            'title': {'required': True},
            'tag': {'required': True},
            'priority': {'required': True},
            'status': {'required': True},
            'description': {'write_only': True}
        }


    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        path = request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        assignee_username = validated_data['assignee']
        assignee = User.objects.get(username = assignee_username)
        issue = Issue.objects.create(
            title=validated_data['title'],
            author=user,
            tag=validated_data['tag'],
            priority=validated_data['priority'],
            status=validated_data['status'],
            description=validated_data['description'],
            project_associated= project,
            assignee = assignee,
        )
        return issue


class CommentListSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'author', 'created_time', 'updated_time', 'description']

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        path = request.path_info
        split_path = path.split('/')
        issue_id = split_path[4]
        issue = Issue.objects.get(id=issue_id)
        comment = Comment.objects.create(
            description=validated_data['description'],
            author=user,
            issue_associated = issue
        )
        return comment


class ProjectDetailSerializer(ModelSerializer):

    issues = IssueListSerializer(many=True)
    contributors = ContributorListSerializer(many=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'type', 'contributors', 'description', 'issues']


class IssueDetailSerializer(ModelSerializer):

    comments = CommentListSerializer(many=True)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'tag', 'priority', 'status', 'author','assignee', 'description', 'comments']


class CommentDetailSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'author', 'created_time', 'updated_time', 'description']


class UserDetailSerializer(ModelSerializer):

    contributions = ContributorListSerializer(many=True)
    issues_created = IssueListSerializer(many=True)
    comments_created = CommentListSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'contributions', 'issues_created', 'comments_created', 'projects_assigned']


class ContributorDetailSerializer(ModelSerializer):
    #
    user_assigned = UserListSerializer()

    class Meta:
        model = Contributor
        fields = ['id', 'user_assigned', 'role', 'permission']



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        print(user)
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        # Add custom claims
        token['username'] = user.username
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name',
                  'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        set_username(user)
        user.save()
        return user
