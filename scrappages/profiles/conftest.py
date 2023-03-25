from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import StringIO
import pytest

@pytest.fixture
def red_image():
    img_io = StringIO.StringIO()
    img = Image.new("RGB", (50, 50), (200, 0, 0))
    img.save(img_io, format="JPG")
    imgf = SimpleUploadedFile("redfile.jpg", img_io.getvalue())

@pytest.fixture
def green_image():
    img_io = StringIO.StringIO()
    img = Image.new("RGB", (50, 50), (0, 200, 0))
    img.save(img_io, format="JPG")
    imgf = SimpleUploadedFile("greenfile.jpg", img_io.getvalue())

@pytest.fixture
def blue_image():
    img_io = StringIO.StringIO()
    img = Image.new("RGB", (50, 50), (0, 0, 200))
    img.save(img_io, format="JPG")
    imgf = SimpleUploadedFile("bluefile.jpg", img_io.getvalue())

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
        username="red",
        password="red12345"
    )

    profile = user.profile
    profile.display_name = "RedGuy420"
    profile.description = "red"
    profile.profile_picture = red_image
    return user

@pytest.fixture
def blue_profile(db, django_user_model, blue_image):
    user = django_user_model.objects.create_user(
        username="blue",
        password="blue12345"
    )

    profile = user.profile
    profile.display_name = "BlueMan69"
    profile.description = "blue"
    profile.profile_picture = blue_image
    return user
