from django.db import models
from django.contrib.auth.models import User


# Create your models here.
def profile_picture_path(instance, filename):
    # MEDIA_ROOT/prof_pics/id__filename
    return f"prof_pics/{instance.user.username}__{filename}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    display_name = models.CharField(
        max_length = 50,
        default=""
    )

    description = models.TextField()

    # ensure only PNG and JPG are allowed
    profile_picture = models.ImageField(
        upload_to=profile_picture_path
    )