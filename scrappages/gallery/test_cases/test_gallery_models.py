from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import os
import pytest
import base64
from gallery.models import get_sentinel_user, Scrap, Comment, Tag

@pytest.mark.django_db
def test_get_sentinel_user():
    user = get_sentinel_user()
    assert user.username == "deleted"

def test_create_scrap(new_user, new_scrap):
    assert Scrap.objects.filter(id=new_scrap.id).exists()
    scrap = Scrap.objects.filter(id=new_scrap.id)[0]

    assert scrap.user == new_user
    assert scrap.title == "Bear"
    assert scrap.description == "Bears!"
    assert scrap.file_type == "text"
    assert scrap.file.url == os.path.join(settings.MEDIA_URL, "uploads/user__bison/newfile.txt")
    
    scrap.file.open("r")
    content = scrap.file.read()
    assert content == "Bears!"
    scrap.file.close()

def test_scrap_serialize(new_scrap):
    context = new_scrap.serialize()
    assert "id" in context # id may or may not change numbers depending on order of tests run
    assert "user" in context and context["user"] == "bison"
    assert "title" in context and context["title"] == "Bear"
    assert "description" in context and context["description"] == "Bears!"
    assert "time_posted" in context
    assert "time_updated" in context
    assert "file_url" in context and context["file_url"] == os.path.join(settings.MEDIA_URL, "uploads/user__bison/newfile.txt")
    assert "file_type" in context and context["file_type"] == "text"
    assert "tags" in context and context["tags"] == []

def test_change_scrap(new_scrap):
    new_scrap.title = "Donkey"
    new_scrap.description = "New Donkey"
    new_scrap.save()

    scrap = get_object_or_404(Scrap, id=new_scrap.id)
    assert scrap.title == "Donkey"
    assert scrap.description == "New Donkey"
    assert scrap.time_posted != scrap.time_updated

def test_create_comment(new_user, new_scrap, new_comment):
    assert Comment.objects.filter(id=new_comment.id).exists()
    comment = Comment.objects.filter(id=new_comment.id)[0]

    assert comment.content == "burrrrr"
    assert comment.user == new_user
    assert comment.scrap == new_scrap
    assert comment.reply_to is None

def test_comment_serialize(new_scrap, new_comment):
    context = new_comment.serialize()

    assert "id" in context
    assert "content" in context and context["content"] == "burrrrr"
    assert "user" in context and context["user"] == "bison"
    assert "scrap_id" in context and context["scrap_id"] == new_scrap.id
    assert "reply_to_id" in context and context["reply_to_id"] is None
    assert "time_posted" in context
    assert "time_updated" in context

def test_another_comment_serialize(new_comment, new_reply):
    context = new_reply.serialize()

    assert "id" in context
    assert "content" in context and context["content"] == "BURRRRRRRRRRRRRR"
    assert "user" in context and context["user"] == "bison"
    assert "scrap_id" in context and context["scrap_id"] == new_comment.scrap.id
    assert "reply_to_id" in context and context["reply_to_id"] == new_comment.id
    assert "time_posted" in context
    assert "time_updated" in context

def test_change_comment(new_comment):
    new_comment.content = "BEAR"
    new_comment.save()

    comment = get_object_or_404(Comment, id=new_comment.id)
    assert comment.content == "BEAR"
    assert comment.time_posted != comment.time_updated

def test_create_tag(new_scrap, new_tag):
    assert Tag.objects.filter(name=new_tag.name, scrap=new_tag.scrap).exists()
    tag = Tag.objects.filter(name=new_tag.name, scrap=new_tag.scrap)[0]

    context = tag.serialize()
    assert "name" in context and context["name"] == "Oregon"
    assert "scrap_id" in context and context["scrap_id"] == new_scrap.id

    assert new_scrap.get_tags() == [context]

def test_delete_user(new_scrap, new_comment):
    new_scrap.user.delete() # same user
    scrap = get_object_or_404(Scrap, id=new_scrap.id)
    assert scrap.user == get_sentinel_user()
    comment = get_object_or_404(Comment, id=new_comment.id)
    assert comment.user == get_sentinel_user()