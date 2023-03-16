from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles.models import Profile


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, display_name=instance.username)


@receiver(post_save, sender=User)
def post_save_save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(pre_delete, sender=User)
def pre_delete_remove_profile_picture(sender, instance, **kwargs):
    instance.profile.delete()
