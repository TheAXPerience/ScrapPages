from django.conf import settings
from django.urls import reverse
import pytest
from profiles.models import Profile

# test access to views
def test_user_profiles_access():
    url = reverse("user_profiles")
    assert url == "/profiles/"

def test_specific_user_profile_access():
    url = reverse("specific_user_profile", kwargs={"username": "bison"})
    assert url == "/profiles/bison"

def test_specific_user_scraps_access():
    url = reverse("specific_user_scraps", kwargs={"username": "bison"})
    assert url == "/profiles/bison/scraps"
