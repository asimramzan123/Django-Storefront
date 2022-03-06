from django.contrib import admin
from . import models 

# Registering our model for admin site
admin.site.register(models.Collection)
admin.site.register(models.Product)



