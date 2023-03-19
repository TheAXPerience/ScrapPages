from django.db import models
from django.contrib.auth.models import User
import datetime

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


# User
#   scraps
#   comments
#   scrap_likes
#   comment_likes

class Scrap(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET(
            get_sentinel_user
        ),
        related_name="scraps"
    )

    title = models.CharField(
        max_length=100
    )

    description = models.TextField(
        default=""
    )

    time_posted = models.DateTimeField(
        auto_now=True
    )

    time_updated = models.DateTimeField(
        auto_now=True
    )

    # only TXT, PNG, JPG, GIF allowed
    file = models.FileField(
        upload_to=user_directory_path
    )

    # in case I need it
    # text or image
    file_type = models.CharField(
        max_length=7,
        default="image"
    )

    likers = models.ManyToManyField(
        User,
        related_name="scrap_likes"
    )

    # comments
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "title": self.title,
            "description": self.description,
            "time_posted": self.time_posted,
            "time_updated": self.time_updated,
            "file_url": self.file.url,
            "file_type": self.file_type,
            "tags": self.get_tags()
        }
        # manually get num_comments, num_likes
    
    def get_tags(self):
        ans = []
        for tag in self.tags:
            ans.append(tag.serialize())
        return ans
    
    def save(self, *args, **kwargs):
        self.time_updated = datetime.datetime.now()
        super(Scrap, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # get and delete file
        try:
            # attempt to delete the file
            if self.file:
                self.file.delete(save=False)
        except:
            # idk the file doesn't exist I suppose
            pass

        super(Scrap, self).delete(*args, **kwargs)


class Comment(models.Model):
    content = models.TextField()

    time_posted = models.DateTimeField(
        auto_now=True
    )

    time_updated = models.DateTimeField(
        auto_now=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET(
            get_sentinel_user
        ),
        related_name="comments"
    )

    scrap = models.ForeignKey(
        'Scrap',
        on_delete=models.CASCADE,
        related_name="comments"
    )

    reply_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        related_name="replies"
    )

    likers = models.ManyToManyField(
        User,
        related_name="comment_likes"
    )

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "user": self.user.username,
            "time_posted": self.time_posted,
            "time_updated": self.time_updated,
            "scrap_id": self.scrap.id,
            "reply_to_id": None if (not self.reply_to) else self.reply_to.id
        }
        # manually get num_likes


class Tag(models.Model):
    name = models.CharField(
        max_length=64
    )

    scrap = models.ForeignKey(
        'Scrap',
        on_delete=models.CASCADE,
        related_name="tags"
    )

    def serialize(self):
        return {
            "name": self.name,
            "scrap_id": self.scrap.id
        }

    # apparently Django only supports single primary keys
    # so this is the alternative
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "scrap"], name="unique_scrap_tag_combination"
            )
        ]
