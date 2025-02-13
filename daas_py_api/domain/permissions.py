from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from manage import logger, config
from rest_framework.permissions import BasePermission, SAFE_METHODS

class FacilityPermission(BasePermission):
    """
    Grants access only if the user has permission for the requested facility.
    """

    def has_permission(self, request, view):
        auth = JWTAuthentication()
        user, token = auth.authenticate(request) or (None, None)

        if not user or not token:
            return False

        # Extract facilities from JWT
        user_facilities = token.get("facility", [])
        # Get requested facility (from query params, headers, or body)
        requested_facility = request.query_params.get("facility")

        if requested_facility not in user_facilities:
            raise PermissionDenied("You do not have access to this facility.")

        return True


class ReadOnlyOrAuthenticatedPermission(BasePermission):
    """
    Allows read-only access for unauthenticated users.
    Requires authentication for write actions.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # Allow GET, HEAD, OPTIONS without authentication
            return True
        return request.user and request.user.is_authenticated