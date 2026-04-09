from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from expo_notifications.api.serializers import DeviceSerializer
from expo_notifications.models import Device


@extend_schema_view(
    list=extend_schema(
        summary="List devices",
        description="Returns all registered devices (push tokens) for the authenticated user.",
    ),
    create=extend_schema(
        summary="Register device",
        description=(
            "Register a push token for the authenticated user. "
            "If the token already exists for the user, the device is reactivated and its language updated."
        ),
    ),
    destroy=extend_schema(
        summary="Delete device",
        description="Remove a registered push token for the authenticated user.",
    ),
)
class DeviceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Manage Expo push tokens for the authenticated user.

    Use `POST /api/devices/` when a user installs the app on a new device to save the
    Expo push token.  Use `DELETE /api/devices/{id}/` when the user logs out or
    uninstalls the app.
    """

    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)
