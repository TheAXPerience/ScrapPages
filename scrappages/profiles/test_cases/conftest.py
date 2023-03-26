from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from PIL import Image
from io import BytesIO
import os
import pytest

@pytest.fixture
def red_image():
    img_io = BytesIO()
    img = Image.new("RGB", (50, 50), (200, 0, 0))
    img.save(img_io, format="JPEG")
    imgf = ContentFile(img_io.getvalue(), "redfile.jpg")
    return imgf

@pytest.fixture
def green_image():
    img_io = BytesIO()
    img = Image.new("RGB", (50, 50), (0, 200, 0))
    img.save(img_io, format="JPEG")
    imgf = ContentFile(img_io.getvalue(), "greenfile.jpg")
    return imgf

@pytest.fixture
def blue_image():
    img_io = BytesIO()
    img = Image.new("RGB", (50, 50), (0, 0, 200))
    img.save(img_io, format="JPEG")
    imgf = ContentFile(img_io.getvalue(), "bluefile.jpg")
    return imgf

@pytest.fixture
def new_user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="bison",
        password="calf123!"
    )
    yield user

@pytest.fixture
def red_profile(db, django_user_model, red_image):
    user = django_user_model.objects.create_user(
        username="redman",
        password="red12345"
    )

    profile = user.profile
    profile.display_name = "RedGuy420"
    profile.description = "red"
    profile.profile_picture = red_image
    user.save()

    yield user
    
    try:
        os.unlink(profile.profile_picture.path)
    except:
        pass


@pytest.fixture
def blue_profile(db, django_user_model, blue_image):
    user = django_user_model.objects.create_user(
        username="blueman",
        password="blue12345"
    )

    profile = user.profile
    profile.display_name = "BlueMan69"
    profile.description = "blue"
    profile.profile_picture = blue_image
    user.save()

    yield user

    try:
        os.unlink(profile.profile_picture.path)
    except:
        pass
