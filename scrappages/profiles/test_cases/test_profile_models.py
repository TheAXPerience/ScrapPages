from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import os
import pytest
import base64
from profiles.models import Profile

@pytest.mark.django_db
def test_create_profile(new_user):
    profile = new_user.profile
    assert new_user.username == profile.display_name
    assert profile.description == ""
    assert profile.get_profile_picture_url() == os.path.join(settings.MEDIA_URL, "profile_pictures/default.jpg")

    assert profile.serialize() == {
        "username": "bison",
        "display_name": "bison",
        "description": "",
        "profile_picture_url": os.path.join(settings.MEDIA_URL, "profile_pictures/default.jpg"),
    }

@pytest.mark.django_db
def test_change_profile(new_user, green_image):
    profile = new_user.profile
    profile.display_name = "Bob"
    profile.description = "He is a Bob, and he will Bob"
    profile.profile_picture = green_image
    new_user.save()

    new_profile = get_object_or_404(Profile, user=profile.user)
    assert new_profile.display_name == "Bob"
    assert new_profile.description == "He is a Bob, and he will Bob"
    assert new_profile.get_profile_picture_url() == os.path.join(settings.MEDIA_URL, "profile_pictures/bison__greenfile.jpg")

    assert new_profile.serialize() == {
        "username": "bison",
        "display_name": "Bob",
        "description": "He is a Bob, and he will Bob",
        "profile_picture_url": os.path.join(settings.MEDIA_URL, "profile_pictures/bison__greenfile.jpg"),
    }
    os.unlink(new_profile.profile_picture.path)

@pytest.mark.django_db
# @pytest.mark.xfail
def test_two_profiles_one_user(new_user):
    try:
        profile = Profile.objects.create(
            user=new_user,
            display_name="Bill",
            description="Bob is Bill"
        )
        assert False
    except IntegrityError:
        assert True
