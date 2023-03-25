from django.core.files.uploadedfile import SimpleUploadedFile
import os
import pytest
from gallery.models import Scrap, Comment, Tag

@pytest.fixture
def new_user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="bison",
        password="calf123!"
    )
    yield user
    # user.delete()

@pytest.fixture
def new_scrap(db, new_user):
    scrap = Scrap.objects.create(
        user=new_user,
        title="Bear",
        description="Bears!",
        file=SimpleUploadedFile("newfile.txt", b"Bears!"),
        file_type="text"
    )
    yield scrap
    os.unlink(scrap.file.path)

@pytest.fixture
def new_comment(db, new_user, new_scrap):
    comment = Comment.objects.create(
        user=new_user,
        scrap=new_scrap,
        content="burrrrr"
    )
    yield comment

@pytest.fixture
def new_reply(db, new_user, new_comment):
    comment = Comment.objects.create(
        user=new_user,
        scrap=new_comment.scrap,
        content="BURRRRRRRRRRRRRR",
        reply_to=new_comment
    )
    yield comment

@pytest.fixture
def new_tag(db, new_scrap):
    tag = Tag.objects.create(
        name="Oregon",
        scrap=new_scrap
    )
    yield tag
