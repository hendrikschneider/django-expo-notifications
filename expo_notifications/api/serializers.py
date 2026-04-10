from rest_framework import serializers

from expo_notifications.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "push_token", "lang", "date_registered", "is_active"]
        read_only_fields = ["id", "date_registered", "is_active"]

    def create(self, validated_data):
        user = self.context["request"].user
        defaults = {
            "is_active": True,
        }
        if "lang" in validated_data:
            defaults["lang"] = validated_data["lang"]

        device, _created = Device.objects.update_or_create(
            user=user,
            push_token=validated_data["push_token"],
            defaults=defaults,
        )
        return device
