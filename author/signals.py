from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """当用户创建或更新时，自动创建或更新对应的UserProfile"""
    if created:
        # 用户新创建时，自动创建UserProfile
        UserProfile.objects.create(user=instance)
    else:
        # 用户更新时，确保UserProfile存在
        try:
            instance.userprofile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)