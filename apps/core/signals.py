import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create user profile when a new user is created.

    This signal ensures that every user has an appropriate profile
    based on their user_type, regardless of how the user was created.

    For academy-related profiles (coach, player, parent), the profile is
    created without academy association initially. The academy association
    should be handled by the view/serializer after creation.
    """
    if created:
        from apps.academies.models import (
            AcademyAdminProfile,
            CoachProfile,
            ExternalClientProfile,
            ParentProfile,
            PlayerProfile,
        )

        profile_classes = {
            "academy_admin": AcademyAdminProfile,
            "coach": CoachProfile,
            "player": PlayerProfile,
            "parent": ParentProfile,
            "external_client": ExternalClientProfile,
        }

        profile_class = profile_classes.get(instance.user_type)

        if profile_class:
            try:
                # Check if profile already exists
                if not hasattr(instance, "profile") or not instance.profile:
                    # Create profile without academy for now
                    # Academy association will be handled by serializers if needed
                    if instance.user_type in ["coach", "player", "academy_admin"]:
                        # These profiles require academy, but we'll create without it first
                        # The serializer will update with academy association
                        profile_class.objects.create(user=instance, academy=None)
                    else:
                        # External client and parent profiles don't require academy
                        profile_class.objects.create(user=instance)

                    logger.info(
                        f"Created {instance.user_type} profile for user: {instance.email}"
                    )
                else:
                    logger.info(f"Profile already exists for user: {instance.email}")
            except Exception as e:
                logger.error(
                    f"Error creating profile for user {instance.email}: {str(e)}"
                )
        else:
            logger.warning(
                f"No profile class found for user_type: {instance.user_type}"
            )


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    """
    Save user profile when user is updated (not created).

    This ensures the profile is saved if any related user data changes.
    """
    if not created and hasattr(instance, "profile") and instance.profile:
        try:
            instance.profile.save()
            logger.debug(f"Updated profile for user: {instance.email}")
        except Exception as e:
            logger.error(f"Error updating profile for user {instance.email}: {str(e)}")
