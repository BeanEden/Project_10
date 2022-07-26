from rest_framework.serializers import ModelSerializer, ValidationError, \
    CharField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from softdesk.models import Project, Issue, Comment, Contributor, set_username

# SERIALIZERS used in this API
# This file manages CRUD operations to have the simplest views possible
# Order of serializers : Lists, Details, Authentication

User = get_user_model()


class UserListSerializer(ModelSerializer):
    """ """
    class Meta:
        model = User
        fields = ['id', 'username']


class ContributorListSerializer(ModelSerializer):
    """ ContributorListSerializer
    Create is overwritten to match the need of the API"""

    class Meta:
        model = Contributor
        fields = ['id', 'user_assigned', 'role',  'permission']

    extra_kwargs = {
        'user_assigned': {'required': True},
        'role': {'required': True},
        'permission': {'required': True}
    }

    def create(self, validated_data):
        """create a Contributor instance"""
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        path = request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        user_assigned = validated_data['user_assigned']
        project = Project.objects.get(id=project_id)
        try:
            user_assigned = User.objects.get(username=user_assigned)
        except:
            raise ValidationError(
                {"user_assigned": "no user with this id"})
        contributor = Contributor.objects.create(
            role=validated_data['role'],
            project_associated=project,
            user_assigned=user_assigned,
            author=user,
            permission=validated_data['permission']
        )
        contributor.save()
        return contributor


class ProjectListSerializer(ModelSerializer):
    """ ContributorListSerializer
    Create is overwritten to match the need of the API"""

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
            title=request.data['title'],
            type=request.data['type'],
            author=user,
            description=request.data['description'],
        )
        contributor = Contributor.objects.create(
            role='author',
            project_associated=project,
            user_assigned=user,
            author=user,
            permission='modify'
        )
        contributor.save()
        return project


class IssueListSerializer(ModelSerializer):
    """ ContributorListSerializer
    Create is overwritten to match the need of the API"""

    class Meta:
        model = Issue
        fields = ['id', 'title', 'tag', 'priority', 'status', 'author',
                  'description', 'assignee']

        extra_kwargs = {
            'title': {'required': True},
            'tag': {'required': True},
            'priority': {'required': True},
            'status': {'required': True},
            'description': {'write_only': True},
            'assignee': {'required': True}
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
        assignee = User.objects.get(username=assignee_username)
        issue = Issue.objects.create(
            title=validated_data['title'],
            author=user,
            tag=validated_data['tag'],
            priority=validated_data['priority'],
            status=validated_data['status'],
            description=validated_data['description'],
            project_associated=project,
            assignee=assignee,
        )
        return issue


class CommentListSerializer(ModelSerializer):
    """ ContributorListSerializer
    Create is overwritten to match the need of the API"""

    class Meta:
        model = Comment
        fields = ['id', 'author', 'created_time', 'updated_time',
                  'description']

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
            issue_associated=issue
        )
        return comment


class ProjectDetailSerializer(ModelSerializer):
    """ ProjectDetailSerializer
        Update and delete are managed through ModelSerializer inheritance
        IssueListSerializer and ContributorListSerializer are linked
        to display"""

    issues = IssueListSerializer(many=True)
    contributors = ContributorListSerializer(many=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'type', 'contributors', 'description',
                  'issues']


class IssueDetailSerializer(ModelSerializer):
    """ IssueDetailSerializer
        Update and delete are managed through ModelSerializer inheritance
        CommentListSerializer is linked to display"""

    comments = CommentListSerializer(many=True)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'tag', 'priority', 'status', 'author',
                  'assignee', 'description', 'comments']


class CommentDetailSerializer(ModelSerializer):
    """ CommentDetailSerializer
        Update and delete are managed through ModelSerializer inheritance"""

    class Meta:
        model = Comment
        fields = ['id', 'author', 'created_time', 'updated_time',
                  'description']


class ContributorDetailSerializer(ModelSerializer):
    """ CommentDetailSerializer
        Update and delete are managed through ModelSerializer inheritance
        UserListSerializer is linked to display"""

    user_assigned = UserListSerializer()

    class Meta:
        model = Contributor
        fields = ['id', 'user_assigned', 'role', 'permission']


# Unused Serializer
class UserDetailSerializer(ModelSerializer):

    contributions = ContributorListSerializer(many=True)
    issues_created = IssueListSerializer(many=True)
    comments_created = CommentListSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'contributions', 'issues_created',
                  'comments_created', 'projects_assigned']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Manages tokens (refresh and access)"""
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        return token


class RegisterSerializer(ModelSerializer):
    """ Manages User creation and validates password checks"""
    password2 = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name',
                  'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True}
        }

    def validate(self, attrs):
        """validates passwords match during sign up"""
        if attrs['password'] != attrs['password2']:
            raise ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """creates a new user"""
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        set_username(user)
        user.save()
        return user
