from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MyUser
from auth_app.models import Profile


@receiver(post_save, sender=MyUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, name=instance.first_name)
#
#
# @receiver(post_save, sender=MyUser)
# def user_to_inactive(sender, instance, created, update_fields, **kwargs):
#     if created:
#         instance.is_active = False
