from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.test.client import encode_multipart, BOUNDARY, MULTIPART_CONTENT
from PIL import Image
import json
import os
import pytest
from gallery.models import Scrap, Comment, Tag

# scraps (GET, POST)
def test_scraps_get():
    pass

def test_scraps_post():
    pass

def test_scraps_post_not_logged_in():
    pass

def test_scraps_post_invalid_title():
    pass

def test_scraps_post_invalid_file():
    pass

# specific_scrap (GET, PUT, DELETE)
def test_specific_scrap_get():
    pass

def test_specific_scrap_does_not_exist():
    pass

def test_specific_scrap_put():
    pass

def test_specific_scrap_put_invalid_title():
    pass

def test_specific_scrap_put_wrong_user():
    pass

def test_specific_scrap_delete():
    pass

def test_specific_scrap_delete_wrong_user():
    pass

# scrap_comments (GET, POST)
def test_scrap_comments_get():
    pass

def test_scrap_comments_does_not_exist():
    pass

def test_scrap_comments_post():
    pass

def test_scrap_comments_post_no_content():
    pass

# specific_scrap_comment (GET, POST, PUT, DELETE)
def test_specific_scrap_comment_get():
    pass

def test_specific_scrap_comment_scrap_does_not_exist():
    pass

def test_specific_scrap_comment_comment_does_not_exist():
    pass

def test_specific_scrap_comment_comment_not_for_scrap():
    pass

def test_specific_scrap_comment_post():
    pass

def test_specific_scrap_comment_post_no_content():
    pass

def test_specific_scrap_comment_put():
    pass

def test_specific_scrap_comment_put_wrong_user():
    pass

def test_specific_scrap_comment_delete():
    pass

def test_specific_scrap_comment_delete_wrong_user():
    pass

# scrap_like (POST, DELETE)
def test_scrap_like_post():
    pass

def test_scrap_like_post_already_exists():
    pass

def test_scrap_like_post_no_user():
    pass

def test_scrap_like_delete():
    pass

def test_scrap_like_delete_does_not_exist():
    pass

def test_scrap_like_delete_no_user():
    pass

# comment_like (POST, DELETE)
def test_comment_like_post():
    pass

def test_comment_like_post_already_exists():
    pass

def test_comment_like_post_no_user():
    pass

def test_comment_like_delete():
    pass

def test_comment_like_delete_does_not_exist():
    pass

def test_comment_like_delete_no_user():
    pass

# scrap_tags (GET, POST, DELETE)
def test_scrap_tags_get():
    pass

def test_scrap_tags_scrap_does_not_exist():
    pass

def test_scrap_tags_post():
    pass

def test_scrap_tags_post_invalid_tag():
    pass

def test_scrap_tags_delete():
    pass

# tagged_scraps (GET)
def test_tagged_scraps_get():
    pass

def test_tagged_scraps_tag_does_not_exist():
    pass