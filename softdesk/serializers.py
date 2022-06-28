from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from softdesk.models import Project, Issue, Comment, Contributor

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth import get_user_model
User = get_user_model()


class ProjectListSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'name', 'author']

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        project = Project.objects.create(
            name = validated_data['name'],
            author = user,
        )

        # contributor = Contributor.objects.create(
        #     role = 'author',
        # )
        # contributor.users_on_project.set(user)
        # project.save()
        # contributor = Contributor.objects.create(
        #     role = 'author'
        # )
        # contributor.users_on_project.add(user)
        # contributor.project_contributed.add(project)
        return project


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'name', 'author']

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        path = request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        issue = Issue.objects.create(
            name=validated_data['name'],
            author=user,
            project_associated= project
        )
        return issue



class CommentListSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'name', 'author']

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
            name=validated_data['name'],
            author=user,
            issue_associated = issue
        )
        return comment




class ProjectDetailSerializer(ModelSerializer):

    issues = IssueListSerializer(many=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'issues']


class IssueDetailSerializer(ModelSerializer):
    comments = CommentListSerializer(many=True)

    class Meta:
        model = Issue
        fields = ['id', 'name', 'comments', 'project_associated']


class CommentDetailSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'name', 'issue_associated']


class UserListSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'name']


class UserDetailSerializer(ModelSerializer):

    project_contributed = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'project_contributed']
    #
    def get_project_contributed(self, instance):
        queryset = instance.project_contributed.all()
        serializer = ProjectListSerializer(queryset, many=True)
        print(serializer)
        return serializer.data


class ContributorListSerializer(ModelSerializer):

    project_contributed = SerializerMethodField()
    users_on_project = SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ['id', 'role', 'project_contributed', 'users_on_project']


class ContributorDetailSerializer(ModelSerializer):

    project_contributed = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'project_contributed']
    #
    def get_project_contributed(self, instance):
        queryset = instance.project_contributed.all()
        serializer = ProjectListSerializer(queryset, many=True)
        print(serializer)
        return serializer.data


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        print(user)
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        # Add custom claims
        token['username'] = user.username
        return token


class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
        )
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name',
                  'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

        # issue.project_associated.set(Project.objects.filter(id=int(pk)))
        # contributor = Contributor.objects.create(
        #     role = 'author',
        # )
        # contributor.users_on_project.set(user)
        # project.save()