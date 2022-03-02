from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tags(models.Model):
    label = models.CharField(max_length=255)


class TaggedItem(models.Model):
    # finding what tag applied to what objects
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    # finding which object is tagged with current tag.
    """ To define generic relationship 3 things we need to define:
    1: should know about taggedItem contentType(video, article, cloth etch)
    2: should know about taggedItem ID for getting record.
    3. reading actual/content object using generic field.
    """
    content_type =models.ForeignKey(ContentType, on_delete=models.CASCADE) #on delete, remove all items.
    object_id = models.PositiveIntegerField()# gen +ve PK, bad for floating PK
    content_obj = GenericForeignKey()

