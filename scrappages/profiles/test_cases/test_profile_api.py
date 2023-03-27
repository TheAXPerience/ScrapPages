from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.test.client import encode_multipart, BOUNDARY, MULTIPART_CONTENT
from PIL import Image
import json
import os
import pytest
from profiles.models import Profile
from gallery.models import Scrap

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

def test_specific_user_profile_put(client, red_profile, green_image):
    logged_in = client.login(username="redman", password="red12345")
    assert logged_in

    data = {
        'display_name': 'kohozuna',
        'description': 'king salmonid #1',
        'profile_picture': green_image
    }

    response = client.put(
        reverse(
            'specific_user_profile',
            kwargs={'username': red_profile.username}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )

    result = json.loads(response.content.decode('utf-8'))
    assert response.status_code == 200
    assert result['display_name'] == 'kohozuna'
    assert result['description'] == 'king salmonid #1'
    assert result['num_scraps'] == 0
    assert result['profile_picture_url'].endswith(os.path.join(settings.MEDIA_URL, "profile_pictures/redman__greenfile.jpg"))
    
    reduser = get_object_or_404(Profile, user=red_profile)
    assert reduser.display_name == result['display_name']
    assert reduser.description == result['description']

    os.unlink(reduser.profile_picture.path)

def test_specific_user_profile_put_invalid_files(client, red_profile, white_image, invalid_image):
    logged_in = client.login(username="redman", password="red12345")
    assert logged_in

    data = {
        'profile_picture': white_image
    }

    response = client.put(
        reverse(
            'specific_user_profile',
            kwargs={'username': red_profile.username}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )

    result = response.content.decode('utf-8')
    assert response.status_code == 400
    assert result == '"Invalid file type; only accepts PNG and JPG"'
    
    data = {
        'profile_picture': invalid_image
    }

    response = client.put(
        reverse(
            'specific_user_profile',
            kwargs={'username': red_profile.username}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )

    result = response.content.decode('utf-8')
    assert response.status_code == 400
    assert result == '"Invalid image file"'

@pytest.mark.parametrize("username, message", [
    ("smol", '"Display name invalid; minimum length = 5"'),
    ("qwaszxerdfcvbnmgjhkltpyouiqpwoieurytjgskhdflzmxcnvbasd", '"Display name invalid; maximum length = 50"'),
    ("noticeme!!!", '"Display name invalid; alphanumeric characters only"')
])
def test_specific_user_profile_put_invalid_display_name(client, red_profile, username, message):
    logged_in = client.login(username="redman", password="red12345")
    assert logged_in

    data = {
        'display_name': username
    }

    response = client.put(
        reverse(
            'specific_user_profile',
            kwargs={'username': red_profile.username}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )

    result = response.content.decode('utf-8')
    assert response.status_code == 400
    assert result == message

def test_specific_user_profile_put_wrong_user(client, red_profile, blue_profile):
    logged_in = client.login(username="blueman", password="blue12345")
    assert logged_in

    data = {
        'display_name': "youbuttface"
    }

    response = client.put(
        reverse(
            'specific_user_profile',
            kwargs={'username': red_profile.username}
        ),
        data=encode_multipart(BOUNDARY, data),
        content_type=MULTIPART_CONTENT
    )

    result = response.content.decode('utf-8')
    assert response.status_code == 400
    assert result == '"You do not have permission to alter another user\'s profile"'

def test_specific_user_profile_delete(client, blue_profile):
    response = client.get(
        reverse(
            'specific_user_profile',
            kwargs={"username": blue_profile.username}
        )
    )
    assert response.status_code == 200

    logged_in = client.login(username="blueman", password="blue12345")
    assert logged_in

    response = client.delete(
        reverse(
            'specific_user_profile',
            kwargs={"username": blue_profile.username}
        )
    )
    assert response.status_code == 200
    assert response.content.decode('utf-8') == 'true'

    response = client.get(
        reverse(
            'specific_user_profile',
            kwargs={"username": blue_profile.username}
        )
    )
    assert response.status_code == 404

def test_specific_user_profile_delete_wrong_user(client, red_profile, blue_profile):
    logged_in = client.login(username="blueman", password="blue12345")
    assert logged_in

    response = client.delete(
        reverse(
            'specific_user_profile',
            kwargs={"username": red_profile.username}
        )
    )
    assert response.status_code == 400
    assert response.content.decode('utf-8') == '"You do not have permission to alter another user\'s profile"'

# specific_user_scraps
# GET
def test_specific_user_scraps(client, red_profile, blue_profile, red_image, green_image, blue_image):
    response = client.get(
        reverse(
            'specific_user_scraps',
            kwargs={'username': red_profile.username}
        )
    )
    assert response.status_code == 200
    assert response.content.decode('utf-8') == '[]'

    s1 = Scrap.objects.create(
        user=red_profile,
        title="red",
        description="red image",
        file=red_image,
        file_type="image"
    )
    s2 = Scrap.objects.create(
        user=red_profile,
        title="green",
        description="green image",
        file=green_image,
        file_type="image"
    )
    s3 = Scrap.objects.create(
        user=blue_profile,
        title="blue",
        description="blue image",
        file=blue_image,
        file_type="image"
    )

    response = client.get(
        reverse(
            'specific_user_scraps',
            kwargs={'username': blue_profile.username}
        )
    )
    assert response.status_code == 200
    result = json.loads(response.content.decode('utf-8'))
    assert len(result) == 1
    assert result[0]['id'] == s3.id

    response = client.get(
        reverse(
            'specific_user_scraps',
            kwargs={'username': red_profile.username}
        )
    )
    assert response.status_code == 200
    result = json.loads(response.content.decode('utf-8'))
    assert len(result) == 2
    assert result[0]['id'] in [s1.id, s2.id]
    assert result[1]['id'] in [s1.id, s2.id]

    s1.delete()
    s2.delete()
    s3.delete()
