from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError

from softdesk.models import Project, Issue, Comment, User


class ProjectListSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'name']


class ProjectDetailSerializer(ModelSerializer):

    issues = SerializerMethodField()
    users_test = SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'issues', 'users_test']

    def get_issues(self, instance):
        queryset = instance.issues.filter(project_associated_id=instance.id)
        print(instance.id)
        serializer = IssueListSerializer(queryset, many=True)
        return serializer.data
    #
    def get_users_test(self, instance):
        queryset = instance.users_test.all()
        serializer = UserListSerializer(queryset, many=True)
        return serializer.data


class IssueListSerializer(ModelSerializer):

    # def __init__(self, project_associated, **kwargs):
    #     super().__init__(**kwargs)
    #     self.project_associated = project_associated

    class Meta:
        model = Issue
        fields = ['id', 'name']


class IssueDetailSerializer(ModelSerializer):

    comments = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'name', 'comments', 'project_associated']

    def get_comments(self, instance):
        queryset= instance.comments.all()
        serializer = CommentListSerializer(queryset, many=True)
        return serializer.data



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