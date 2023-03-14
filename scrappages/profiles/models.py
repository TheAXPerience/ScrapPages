from django.db import models
from django.contrib.auth.models import User


# Create your models here.
def profile_picture_path(instance, filename):
    # MEDIA_ROOT/prof_pics/id__filename
    return f"prof_pics/{instance.user.get_username()}__{filename}"


# User class
# username - max_length = 150, characters = alphanumeric and "_@+.-"
# password - stored as a hash
# email
# first_name - max_length = 150
# last_name - max_length = 150

# User.check_pasword(raw_password)
# User.set_password(raw_password)
# User.set_unusable_password() - use for "deleted" user account
# User.get_username()

# there are more fields and methods for permissions, but every user here is gonna have basic ones so

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