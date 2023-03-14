from django.db import models
from django.contrib.auth.models import User


# Create your models here.
def user_directory_path(instance, filename):
    # MEDIA_ROOT/uploads/user__id/filename
    return f"uploads/user__{instance.user.username}/{filename}"

# set user to "deleted"
def get_sentinel_user():
    from django.contrib.auth import get_user_model

    return get_user_model().objects.get_or_create(
        username="deleted"
    )[0]


class Scrap(models.Model):
    user = models.ForeignKeyField(
        User,
        on_delete = models.SET(
            get_sentinel_user
        ),
        related_name = "scraps"
    )

    title = models.CharField(
        max_length = 100
    )

    description = models.TextField()

    time_posted = models.DateTimeField(
        auto_now=True
    )

    time_updated = models.DateTimeField(
        auto_now=True
    )

    # only TXT, PNG, JPG, GIF allowed
    file = models.FileField(
        upload_to = user_directory_path
    )

    # in case I need it
    # text or image
    file_type = models.CharField(
        max_length = 7,
        default = "image"
    )

    likers = models.ManyToManyField(
        User,
        related_name = "scrap_likes"
    )


class Comment(models.Model):
    content = models.TextField()

    time_posted = models.DateTimeField(
        auto_now=True
    )

    time_updated = models.DateTimeField(
        auto_now=True
    )

    user = models.ForeignKeyField(
        User,
        on_delete = models.SET(
            get_sentinel_user
        ),
        related_name = "+"
    )

    scrap = models.ForeignKeyField(
        'Scrap',
        on_delete = models.CASCADE,
        related_name = "comments"
    )

    reply_to = models.ForeignKeyField(
        'self',
        on_delete = models.CASCADE,
        null = True,
        related_name = "replies"
    )

    likers = models.ManyToManyField(
        User,
        related_name = "comment_likes"
    )


class Tag(models.Model):
    name = models.CharField(
        max_length = 64
    )

    scrap = models.ForeignKeyField(
        'Scrap',
        on_delete = models.CASCADE,
        related_name = "tags"
    )

    # apparently Django only supports single primary keys
    # so this is the alternative
    class Meta:
        constraints = [
            models.UniqueConstraint(
                files=["name", "scrap"], name="unique_scrap_tag_combination"
            )
        ]