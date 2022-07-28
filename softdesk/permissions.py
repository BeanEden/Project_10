from rest_framework import permissions
from softdesk.models import Contributor, Project


class IsAllowedOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `author` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `author`.
        if obj.author == request.user:
            return True

        else:
            path = request.path_info
            split_path = path.split('/')
            project_id = split_path[2]
            project = Project.objects.get(id=project_id)
            user = request.user
            try:
                contributor = Contributor.objects.get(
                    user_assigned=user,
                    project_associated=project)
                return contributor.permission == 'modify'
            except Contributor.DoesNotExist:
                return False
            except Contributor.MultipleObjectsReturned:
                return False
        # else:
        #     return False
