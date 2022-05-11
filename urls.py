from django.urls import path
from rest_framework import routers

from .api import api_view
from .views import *

urlpatterns = [
    path("", post_list, name="index"),
    path("create", post_create, name="create_post"),
    path("post/<str:slug>/", post_detail, name="post_view_url"),
    path("rate_post/<str:slug>/", rate_post, name="rate_post"),
    path("rate_comment/<str:slug>/", rate_comment, name="rate_comment"),
    path("menad", menadus, name="menad"),
    path("top", top_post_list, name="top"),
    path("top_comment", top_comment_post_list, name="top_comment"),
]

router = routers.SimpleRouter()
router.register(r'api', api_view.PostViewSet, basename='post_api')

urlpatterns += router.urls
