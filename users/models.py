from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)

    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    