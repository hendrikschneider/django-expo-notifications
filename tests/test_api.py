import pytest
from django.urls import reverse

from expo_notifications.models import Device
from tests.factories import ActiveDeviceFactory, DeviceFactory, UserFactory


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


# ── list ──────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_list_devices_requires_authentication(api_client):
    url = reverse("device-list")
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_list_devices_returns_only_own_devices(auth_client, user):
    own_device = DeviceFactory(user=user)
    DeviceFactory()  # another user's device

    url = reverse("device-list")
    response = auth_client.get(url)

    assert response.status_code == 200
    ids = [d["id"] for d in response.data]
    assert ids == [own_device.pk]


@pytest.mark.django_db
def test_list_devices_returns_correct_fields(auth_client, user):
    device = ActiveDeviceFactory(user=user)

    url = reverse("device-list")
    response = auth_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    data = response.data[0]
    assert data["id"] == device.pk
    assert data["push_token"] == device.push_token
    assert data["lang"] == device.lang
    assert data["is_active"] == device.is_active


# ── create ─────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_register_device_requires_authentication(api_client):
    url = reverse("device-list")
    response = api_client.post(url, {"push_token": "ExponentPushToken[abc123]"})
    assert response.status_code == 403


@pytest.mark.django_db
def test_register_device_creates_device(auth_client, user):
    url = reverse("device-list")
    response = auth_client.post(url, {"push_token": "ExponentPushToken[abc123]"})

    assert response.status_code == 201
    assert Device.objects.filter(user=user, push_token="ExponentPushToken[abc123]").exists()


@pytest.mark.django_db
def test_register_device_with_lang(auth_client, user):
    url = reverse("device-list")
    response = auth_client.post(
        url,
        {"push_token": "ExponentPushToken[abc123]", "lang": "en-US"},
    )

    assert response.status_code == 201
    assert response.data["lang"] == "en-US"


@pytest.mark.django_db
def test_register_device_returns_created_device(auth_client, user):
    url = reverse("device-list")
    response = auth_client.post(url, {"push_token": "ExponentPushToken[abc123]"})

    assert response.status_code == 201
    data = response.data
    assert "id" in data
    assert data["push_token"] == "ExponentPushToken[abc123]"
    assert data["is_active"] is True


@pytest.mark.django_db
def test_register_device_reactivates_existing_token(auth_client, user):
    existing = DeviceFactory(user=user, push_token="ExponentPushToken[abc123]", is_active=False)

    url = reverse("device-list")
    response = auth_client.post(url, {"push_token": "ExponentPushToken[abc123]"})

    assert response.status_code == 201
    existing.refresh_from_db()
    assert existing.is_active is True
    assert Device.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_register_device_requires_push_token(auth_client):
    url = reverse("device-list")
    response = auth_client.post(url, {})

    assert response.status_code == 400
    assert "push_token" in response.data


# ── destroy ────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_delete_device_requires_authentication(api_client, user):
    device = DeviceFactory(user=user)
    url = reverse("device-detail", kwargs={"pk": device.pk})
    response = api_client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_device_removes_own_device(auth_client, user):
    device = DeviceFactory(user=user)
    url = reverse("device-detail", kwargs={"pk": device.pk})
    response = auth_client.delete(url)

    assert response.status_code == 204
    assert not Device.objects.filter(pk=device.pk).exists()


@pytest.mark.django_db
def test_delete_device_cannot_delete_other_users_device(auth_client):
    other_device = DeviceFactory()  # belongs to a different user
    url = reverse("device-detail", kwargs={"pk": other_device.pk})
    response = auth_client.delete(url)

    assert response.status_code == 404
    assert Device.objects.filter(pk=other_device.pk).exists()


# ── schema ─────────────────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_openapi_schema_is_accessible(client):
    url = reverse("schema")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_redoc_is_accessible(client):
    url = reverse("redoc")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_swagger_ui_is_accessible(client):
    url = reverse("swagger-ui")
    response = client.get(url)
    assert response.status_code == 200
