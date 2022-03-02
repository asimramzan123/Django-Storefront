from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class LikedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type =models.ForeignKey(ContentType, on_delete=models.CASCADE) #on user delete, remove all user liked items.
    object_id = models.PositiveIntegerField()# gen +ve PK, bad for floating PK
    content_obj = GenericForeignKey()


