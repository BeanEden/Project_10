from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from softdesk.models import Project, Issue, Comment, Contributor

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_slug

from django.contrib.auth import get_user_model
User = get_user_model()


def clean_string(string, *args):
    string = string.casefold()
    for i in args:
        string = string.replace(i, "")
    return string



class ProjectListSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'title','type', 'author', 'description']

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
        return project


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'title', 'tag', 'priority', 'author', 'description']

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
        fields = ['id', 'username']


class UserDetailSerializer(ModelSerializer):

    project_contributed = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'project_contributed']
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

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        path = request.path_info
        split_path = path.split('/')
        project_id = split_path[2]
        project = Project.objects.get(id=project_id)
        print(validated_data)
        # user = User.objects.get(username=validated_data['username'])
        contributor = Contributor.objects.create(
            role = validated_data['role'],
            # users_on_project = user,
            # project_contributed = project
        )
        # contributor.users_on_project.set(user)
        # project.save()
        # contributor = Contributor.objects.create(
        #     role = 'author'
        # )
        # contributor.users_on_project.add(user)
        contributor.project_contributed.add(project)
        return contributor

    def get_project_contributed(self, instance):
        queryset = instance.project_contributed.all()
        serializer = ProjectListSerializer(queryset, many=True)
        print(serializer)
        return serializer.data

    def get_users_on_project(self, instance):
        queryset = instance.users_on_project.all()
        serializer = UserListSerializer(queryset, many=True)
        print(serializer)
        return serializer.data

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

    # username = SerializerMethodField()
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
        )
    # first_name = serializers.CharField(validators=[validate_slug])
    # last_name = serializers.CharField(validators=[validate_slug])

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
        username = self.username_creation(validated_data)
        # count = 0
        # if User.objects.get(username=username) :
        #     count+=1
        #     username = username + str(count)

        print(username)
        user = User.objects.create(
            username = username,
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


    def username_creation(self, validated_data):
        clean_first_name = clean_string(validated_data['first_name']," ","-")
        clean_last_name = clean_string(validated_data['last_name']," ","-")

        if len(clean_first_name) < 4:
            first_key = clean_first_name

        else :
            first_key = clean_first_name[:3]


        if len(clean_last_name) < 2:
            second_key = clean_last_name

        else:
            second_key = clean_last_name[:2]

        username = first_key+second_key

        return username
