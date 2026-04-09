from rest_framework import serializers

from expo_notifications.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "push_token", "lang", "date_registered", "is_active"]
        read_only_fields = ["id", "date_registered", "is_active"]

    def create(self, validated_data):
        user = self.context["request"].user
        device, _ = Device.objects.update_or_create(
            user=user,
            push_token=validated_data["push_token"],
            defaults={
                "lang": validated_data.get("lang", ""),
                "is_active": True,
            },
        )
        return device
