import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.


def profile_picture_path(instance, filename):
    # MEDIA_ROOT/prof_pics/id__filename
    return f"profile_pictures/{instance.user.get_username()}__{filename}"


def validate_profile_picture(image):
    return True

# User class
# username - max_length = 150, characters = alphanumeric and "_@+.-"
# password - stored as a hash
# email
# first_name - max_length = 150
# last_name - max_length = 150

# User.check_password(raw_password)
# User.set_password(raw_password)
# User.set_unusable_password() - use for "deleted" user account
# User.get_username()

# there are more fields and methods for permissions, but every user here is gonna have basic ones so


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.DO_NOTHING,
        primary_key=True,
    )

    display_name = models.CharField(
        max_length=50,
        default=""
    )

    description = models.TextField(
        default=""
    )

    # ensure only PNG and JPG are allowed
    profile_picture = models.ImageField(
        upload_to=profile_picture_path,
        blank=True,
        null=True
    )

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url

        # TODO: set up default image + image path
        return os.path.join(settings.MEDIA_URL, "profile_pictures/default.jpg")

    def serialize(self):
        return {
            "username": self.user.username,
            "display_name": self.display_name,
            "description": self.description,
            "profile_picture_url": self.get_profile_picture_url(),
        }

    def save(self, *args, **kwargs):
        # delete previous profile picture if new one is saved
        try:
            this = Profile.objects.get(user=self.user)
            if this.profile_picture != self.profile_picture:
                this.profile_picture.delete(save=False)
                # os.remove(os.path.join(settings.MEDIA_ROOT,
                #           this.profile_picture.url))

                # storage, path = this.profile_picture.storage, this.profile_picture.path
                # storage.delete(path)

        except:
            # idk it worked I suppose
            pass

        # call superclass's save()
        super(Profile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # get and delete file
        try:
            # attempt to delete the file
            if self.profile_picture:
                self.profile_picture.delete(save=False)
        except:
            # idk the file doesn't exist I suppose
            pass

        # call superclass's delete()
        super(Profile, self).delete(*args, **kwargs)
