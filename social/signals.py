from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserConnection, Like, Comment, Post, Activity
from user.models import UserProfile

@receiver(post_save, sender=UserConnection)
def update_follow_counts(sender, instance, created, **kwargs):
    """Update follower and following counts when a UserConnection is created"""
    if created:
        # Update follower's following count
        follower_profile = UserProfile.objects.get(user=instance.follower)
        follower_profile.following_count = UserConnection.objects.filter(follower=instance.follower).count()
        follower_profile.save()

        # Update following's followers count
        following_profile = UserProfile.objects.get(user=instance.following)
        following_profile.followers_count = UserConnection.objects.filter(following=instance.following).count()
        following_profile.save()

@receiver(post_delete, sender=UserConnection)
def update_follow_counts_delete(sender, instance, **kwargs):
    """Update follower and following counts when a UserConnection is deleted"""
    # Update follower's following count
    follower_profile = UserProfile.objects.get(user=instance.follower)
    follower_profile.following_count = UserConnection.objects.filter(follower=instance.follower).count()
    follower_profile.save()

    # Update following's followers count
    following_profile = UserProfile.objects.get(user=instance.following)
    following_profile.followers_count = UserConnection.objects.filter(following=instance.following).count()
    following_profile.save()

@receiver(post_save, sender=Like)
def update_likes_count(sender, instance, created, **kwargs):
    """Update post likes count when a Like is created"""
    if created:
        post = instance.post
        post.likes_count = Like.objects.filter(post=post).count()
        post.save()
        # Create activity record
        Activity.objects.create(
            user=instance.user,
            activity_type='like',
            content_id=post.id,
            details={'post_id': post.id, 'post_author': post.author.username}
        )

@receiver(post_delete, sender=Like)
def update_likes_count_delete(sender, instance, **kwargs):
    """Update post likes count when a Like is deleted"""
    post = instance.post
    post.likes_count = Like.objects.filter(post=post).count()
    post.save()

@receiver(post_save, sender=Comment)
def update_comments_count(sender, instance, created, **kwargs):
    """Update post comments count when a Comment is created"""
    if created:
        post = instance.post
        post.comments_count = Comment.objects.filter(post=post).count()
        post.save()
        # Create activity record
        Activity.objects.create(
            user=instance.user,
            activity_type='comment',
            content_id=post.id,
            details={'post_id': post.id, 'post_author': post.author.username, 'comment_content': instance.content[:100]}
        )

@receiver(post_delete, sender=Comment)
def update_comments_count_delete(sender, instance, **kwargs):
    """Update post comments count when a Comment is deleted"""
    post = instance.post
    post.comments_count = Comment.objects.filter(post=post).count()
    post.save()

@receiver(post_save, sender=Post)
def create_post_activity(sender, instance, created, **kwargs):
    """Create activity record when a Post is created"""
    if created:
        Activity.objects.create(
            user=instance.author,
            activity_type='post',
            content_id=instance.id,
            details={'post_content': instance.content[:100]}
        ) 