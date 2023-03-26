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

@pytest.fixture
def user1(db, django_user_model):
    return User.objects.create_user(
        username="pooky",
        password="pooky123"
    )

@pytest.fixture
def user2(db, django_user_model):
    return User.objects.create_user(
        username="silver",
        password="silver123"
    )

@pytest.fixture
def yellow_png():
    img_io = BytesIO()
    img = Image.new("RGB", (50, 50), (200, 200, 0))
    img.save(img_io, format="PNG")
    imgf = ContentFile(img_io.getvalue(), "yellowfile.png")
    return imgf

@pytest.fixture
def cyan_gif():
    img_io = BytesIO()
    img = Image.new("RGB", (50, 50), (0, 200, 200))
    img.save(img_io, format="GIF")
    imgf = ContentFile(img_io.getvalue(), "cyanfile.gif")
    return imgf

@pytest.fixture
def violet_jpg():
    img_io = BytesIO()
    img = Image.new("RGB", (50, 50), (200, 0, 200))
    img.save(img_io, format="JPEG")
    imgf = ContentFile(img_io.getvalue(), "viofile.jpg")
    return imgf

@pytest.fixture
def white_pdf():
    img_io = BytesIO()
    img = Image.new("RGB", (50, 50), (200, 200, 200))
    img.save(img_io, format="PDF")
    imgf = ContentFile(img_io.getvalue(), "whitefile.pdf")
    return imgf

@pytest.fixture
def txt_file():
    return ContentFile("black", 'blackfile.txt')

@pytest.fixture
def md_file():
    return ContentFile("grey", "greyfile.md")

@pytest.feature
def scrap1(user1, yellow_png):
    scrap = Scrap.objects.create(
        user=user1,
        title="Yellow",
        description="Yellow fellow",
        file=yellow_png,
        file_type="image"
    )

    yield scrap

    try:
        os.unlink(scrap.file.path)
    except:
        pass

@pytest.feature
def scrap2(user1, cyan_gif):
    scrap = Scrap.objects.create(
        user=user1,
        title="Cyan",
        description="Cyan I can",
        file=cyan_gif,
        file_type="image"
    )

    yield scrap

    try:
        os.unlink(scrap.file.path)
    except:
        pass

@pytest.feature
def scrap3(user2, txt_file):
    scrap = Scrap.objects.create(
        user=user2,
        title="Black",
        description="Black is back",
        file=txt_file,
        file_type="txt"
    )

    yield scrap

    try:
        os.unlink(scrap.file.path)
    except:
        pass

@pytest.fixture
def comment1(user1, scrap1):
    comment = Comment.objects.create(
        user=user1,
        scrap=scrap1,
        content="Lemony yellow",
        reply_to=False
    )

    yield comment

@pytest.fixture
def comment2(user2, scrap1):
    comment = Comment.objects.create(
        user=user2,
        scrap=scrap1,
        content="mellow yellow",
        reply_to=False
    )

    yield comment

@pytest.fixture
def reply1(user2, comment1):
    comment = Comment.objects.create(
        user=user2,
        scrap=comment1.scrap,
        content="Leomny Salmonly Yellow",
        reply_to=comment1
    )

    yield comment

@pytest.fixture
def tags1(scrap1):
    tags = []

    tags.append(Tag.objects.create(
        name="yellow",
        scrap=scrap1
    ))
    tags.append(Tag.objects.create(
        name="pic",
        scrap=scrap1
    ))
    
    yield tags

@pytest.fixture
def tags2(scrap2):
    tags = []
    tags.append(Tag.objects.create(
        name="pic",
        scrap=scrap1
    ))
    tags.append(Tag.objects.create(
        name="cyan",
        scrap=scrap2
    ))
    tags.append(Tag.objects.create(
        name="aqua",
        scrap=scrap2
    ))
    
    yield tags
