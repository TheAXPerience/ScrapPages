from django.conf import settings
from django.urls import reverse
from PIL import Image
import json
import os
import pytest
from profiles.models import Profile


# user_profiles
# GET, POST
def test_user_profiles_get(client, red_profile):
    response = client.get(reverse("user_profiles"))
    result = json.loads(response.content.decode("utf-8"))
    assert len(result) == 1

    rps = red_profile.profile.serialize()
    assert result[0]["username"] == rps["username"]
    assert result[0]["display_name"] == rps["display_name"]
    assert result[0]["description"] == rps["description"]

    m = len(result[0]["profile_picture_url"])
    n = len(rps["profile_picture_url"])
    assert result[0]["profile_picture_url"][m-n:] == rps["profile_picture_url"]

@pytest.mark.django_db
def test_user_profiles_post(client):
    data = {
        "username": "greenman",
        "password": "unassumingpassword"
    }
    response = client.post(
        reverse("user_profiles"),
        data,
        content_type="application/json"
    )

    assert response.status_code == 200
    
    result = json.loads(response.content.decode("utf-8"))
    assert result["username"] == "greenman"
    assert result["display_name"] == "greenman"
    assert result["description"] == ""
    
    m = len(result["profile_picture_url"])
    default_path = os.path.join(settings.MEDIA_URL, "profile_pictures/default.jpg")
    n = len(default_path)
    assert result["profile_picture_url"][m-n:] == default_path

def test_user_profiles_post_already_exists(client, red_profile, blue_profile):
    data = {
        "username": "redman",
        "password": "unassumingpassword"
    }
    response = client.post(reverse("user_profiles"), data, content_type="application/json")

    assert response.content.decode("utf-8") == '"Username already exists"'
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.parametrize("username, password, message", [
    ("qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm1234567890", "dummythicc", '"Username too long; maximum length = 50"'),
    ("hi", "imbobhowboutchu", '"Username too short; minimum length = 5"'),
    ("iamlongenough", "notme", '"Password too short; minimum length = 8"'),
    ("belonger", "qwertyuiopasdfghjklzxcvbnm1234567890qwertyuiopasdfghjklzxcvbbnm123456789012345678900987654321", '"Password too long; maximum length = 70"')
])
def test_user_profiles_post_username_password_limits(client, username, password, message):
    data = {
        "username": username,
        "password": password
    }
    response = client.post(reverse("user_profiles"), data, content_type="application/json")

    assert response.content.decode("utf-8") == message
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.parametrize("username", ["hi i have spaces", "hello!!!!!!", "i[}{]*73df28(u)"])
def test_user_profiles_invalid_usernames(client, username):
    data = {
        "username": username,
        "password": "okpassword123"
    }
    response = client.post(
        reverse("user_profiles"),
        data,
        content_type="application/json"
    )

    message = '"Username invalid; alphanumeric characters only"'
    assert response.content.decode("utf-8") == message
    assert response.status_code == 400

# specific_user_profile
# GET, PUT, DELETE
def test_specific_user_profile_get(client, red_profile, blue_profile):
    response = client.get(
        reverse(
            "specific_user_profile",
            kwargs={"username": red_profile.username}
        )
    )
    result = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 200
    assert result["username"] == red_profile.username
    assert result["display_name"] == red_profile.profile.display_name
    assert result["description"] == red_profile.profile.description

    m = len(result["profile_picture_url"])
    n = red_profile.profile.get_profile_picture_url()
    assert result["profile_picture_url"][m-len(n):] == n


    response = client.get(
        reverse(
            "specific_user_profile",
            kwargs={"username": blue_profile.username}
        )
    )
    result = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 200
    assert result["username"] == blue_profile.username
    assert result["display_name"] == blue_profile.profile.display_name
    assert result["description"] == blue_profile.profile.description

    m = len(result["profile_picture_url"])
    n = blue_profile.profile.get_profile_picture_url()
    assert result["profile_picture_url"][m-len(n):] == n

@pytest.mark.django_db
def test_specific_user_profile_unassigned_username(client):
    response = client.get(
        reverse(
            "specific_user_profile",
            kwargs={"username": "idonotexist"}
        )
    )

    assert response.status_code == 404

def test_specific_user_profile_put(client, red_profile):
    pass

@pytest.mark.parametrize("username, message", [
    ("smol", '"Display name invalid; minimum length = 5"'),
    ("qwaszxerdfcvbnmgjhkltpyouiqpwoieurytjgskhdflzmxcnvbasd", '"Display name invalid; maximum length = 50"'),
    ("noticeme!!!", '"Display name invalid; alphanumeric characters only"')
])
def test_specific_user_profile_put_invalid_display_name(client, red_profile, username, message):
    pass

def test_specific_user_profile_put_wrong_user(client, red_profile, blue_profile):
    pass

def test_specific_user_profile_delete(client, blue_profile):
    pass

def test_specific_user_profile_delete_wrong_user(client, red_profile, blue_profile):
    pass

# specific_user_scraps
# GET
def test_specific_user_scraps(client, red_profile):
    pass