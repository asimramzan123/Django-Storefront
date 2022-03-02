from django.urls import URLPattern, path
from . import views # getting view from current directory


# adding url configurations
urlpatterns = [
    path('hello/', views.hello)
]