from rest_framework import generics, viewsets
from rest_framework.response import Response

from main.api.serializers import PostSerializer
from main.models import Post


class PostViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)
