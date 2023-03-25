from django.conf import settings
from django.urls import reverse
import pytest

# test access to views
def test_scraps_access():
    url = reverse("scraps")
    assert url == "/scraps/"

def test_specific_scrap_access():
    url = reverse("specific_scrap", kwargs={"sid": 2})
    assert url == "/scraps/2"

def test_scrap_comments_access():
    url = reverse("scrap_comments", kwargs={"sid": 4})
    assert url == "/scraps/4/comments"

def test_specific_scrap_comment_access():
    url = reverse("specific_scrap_comment", kwargs={"sid": 4, "cid": 7})
    assert url == "/scraps/4/comments/7"

def test_scrap_like_access():
    url = reverse("scrap_like", kwargs={"sid": 5})
    assert url == "/scraps/5/like"

def test_comment_like_access():
    url = reverse("comment_like", kwargs={"sid": 3, "cid": 3})
    assert url == "/scraps/3/comments/3/like"

def test_scrap_tags_access():
    url = reverse("scrap_tags", kwargs={"sid": 1})
    assert url == "/scraps/1/tags"

def test_tagged_scraps_access():
    url = reverse("tagged_scraps", kwargs={"tname": "barbara"})
    assert url == "/scraps/tagged/barbara"
