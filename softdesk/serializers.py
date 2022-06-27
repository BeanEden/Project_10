from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from softdesk.models import Project, Issue, Comment, User, Contributor

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


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
        return project


class ProjectDetailSerializer(ModelSerializer):

    issues = SerializerMethodField()
    # contributors = SerializerMethodField()
    # issues = IssueListSerializer(many=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'issues']

    def get_issues(self, instance):
        queryset = instance.issues.filter(project_associated_id=instance.id)
        print(instance.id)
        serializer = IssueListSerializer(queryset, many=True)
        return serializer.data

    # def get_contributors(self, instance):
    #     queryset = instance.contributors.all()
    #     queryset = Contributor.objects.filter(project_contributed= instance.id)
    #     serializer = ContributorListSerializer(queryset, many=True)
    #     return serializer.data

    # def create(self, validated_data):
    #     print(validated_data)
    #     user = None
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         user = request.user
    #     project=Project.objects.create(
    #         name = validated_data['name'],
    #         author = user,
    #     )
    #     contributor = Contributor.objects.create(
    #         role = 'author',
    #         project_contributed = project.id,
    #         users_on_project = user,
    #     )
    #     project.save()
    #     return project

    # def create(self, validated_data):
    #     project, created = Project.objects.update_or_create(
    #         question=validated_data.get('question', None),
    #         defaults={'name': validated_data.get('name', None),
    #                   'author':'ter'})
    #     return project


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'name', 'author']

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        print(request.data)
        pk = request.path_info
        pk = pk.replace('/projects/', "")
        pk = pk.replace('/issues/', "")
        project=Project.objects.get(id=pk)
        issue = Issue.objects.create(
            name=validated_data['name'],
            author=user,
            project_associated= project
        )
        # issue.project_associated.set(Project.objects.filter(id=int(pk)))
        # contributor = Contributor.objects.create(
        #     role = 'author',
        # )
        # contributor.users_on_project.set(user)
        # project.save()
        return issue


class IssueDetailSerializer(ModelSerializer):

    comments = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'name', 'comments', 'project_associated']

    def get_comments(self, instance):
        queryset = instance.comments.all()
        serializer = CommentListSerializer(queryset, many=True)
        return serializer.data

    def create(self, validated_data):
        return Issue.objects.create(**validated_data)


class CommentListSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'name']



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
    #
    # def get_project_contributed(self, instance):
    #     queryset = instance.project_contributed.all()
    #     serializer= C

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