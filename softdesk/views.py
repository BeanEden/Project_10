from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from softdesk.models import Project, Issue, Comment
from softdesk.serializers import ProjectListSerializer, ProjectDetailSerializer,\
    IssueListSerializer, IssueDetailSerializer,\
    CommentListSerializer, CommentDetailSerializer

from django.contrib.auth.models import User

class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectViewset(MultipleSerializerMixin, ReadOnlyModelViewSet):

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):

        return Project.objects.all()

    def post(self, request):
        serializer = ProjectDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        project = Project.objects.filter(id=pk)
        item = Project.objects.filter(id=pk)
        item.delete()
        serializer = ProjectDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = Project.objects.filter(id=pk)
        item.delete()
        return Response({"status": "success", "data":"item successfully erased"},
                        status=status.HTTP_200_OK)


class IssueViewset(MultipleSerializerMixin, ReadOnlyModelViewSet):

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    # queryset = Issue.objects.filter(project_id='project_id')

    def get_queryset(self):

        return Issue.objects.all()

    # def get_queryset(self):
    #     portfolio = Account.objects.get(id=self.request.account.pk)
    #     # ... do something
    #     identifiers = Identifier.objects.filter(
    #         account=self.request.account.pk)
    #     return identifiers


    def post(self, request, project_id):
        test = request.data
        test = test.copy()
        test['project_associated'] = project_id
        serializer = IssueDetailSerializer(data=test)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk, project_id):
        item = Issue.objects.filter(id=pk)
        item.delete()
        test = request.data
        test = test.copy()
        print(pk, project_id)
        test['project_associated'] = project_id
        test['id'] = pk
        print(test)
        serializer = IssueDetailSerializer(data=test)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, project_id):
        item = Issue.objects.filter(id=pk)
        item.delete()
        return Response({"status": "success", "data":"item successfully erased"},
                        status=status.HTTP_200_OK)


class CommentViewset(ReadOnlyModelViewSet):

    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer

    # def get_queryset(self):
    #     queryset = Comment.objects.filter(issue_id=self.request.pk)
    #     issue_id = self.request.GET.get('issue_id')
    #     if issue_id:
    #         queryset = queryset.filter(issue_id=issue_id)
    #     return queryset

    def get_queryset(self):
        return Comment.objects.all()

    def post(self, request, issue_id, project_id):
        test = request.data
        test = test.copy()
        print(project_id, issue_id)
        test['issue_associated'] = issue_id
        serializer = CommentDetailSerializer(data=test)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, issue_id, project_id):
        item = Comment.objects.filter(id=issue_id)
        test = request.data
        test = test.copy()
        test['issue_associated'] = issue_id
        serializer = CommentDetailSerializer(data=test)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, project_id, issue_id):
        item = Comment.objects.filter(id=pk)
        item.delete()
        return Response({"status": "success", "data":"item successfully erased"},
                        status=status.HTTP_200_OK)



class UserViewset(ReadOnlyModelViewSet):

    def get_queryset(self):
        return User.objects.all()

    def post(self, request, project_id, issue_id):
        test = request.data
        test = test.copy()
        print(issue_id)
        test['issue_associated'] = issue_id
        serializer = CommentDetailSerializer(data=test)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, pk, project_id, issue_id):
    #     item = Comment.objects.filter(id=pk)
    #     test = request.data
    #     test = test.copy()
    #     test['issue_associated'] = issue_id
    #     serializer = CommentDetailSerializer(data=test)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({"status": "success", "data": serializer.data},
    #                         status=status.HTTP_200_OK)
    #     else:
    #         return Response({"status": "error", "data": serializer.errors},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #
    #
    # def delete(self, request, pk, project_id, issue_id):
    #     item = Comment.objects.filter(id=pk)
    #     item.delete()
    #     return Response({"status": "success", "data":"item successfully erased"},
    #                     status=status.HTTP_200_OK)