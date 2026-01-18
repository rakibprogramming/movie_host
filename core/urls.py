from django.urls import path
from . import views
from .stream import stream_video
from .stream import stream_subtitle
from ..add_file import start_download, download_status, add

from django.urls import re_path

 
urlpatterns = [
    path('view', views.view, name='view'),
    path('', views.home, name='home'),
    re_path(r'^movies/(?P<filename>.+?)/?$', stream_video, name='stream_video'),
    path('subs/<path:filename>', stream_subtitle, name='stream_subtitle'),
    path('add_subtitle/', views.add_subtitle, name='add_subtitle'),
    path('delete_video/', views.delete_video, name='delete_video'),
    path('start_download/', start_download, name='start_download'),
    path('download_status/', download_status, name='download_status'),
    path("add", add)
    
]   