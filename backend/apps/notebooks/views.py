from django.db import models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notebook
from .pagination import NotebookPagination
from .serializers import (
    NotebookCreateSerializer,
    NotebookSerializer,
    NotebookUpdateSerializer,
)


class NotebookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = NotebookPagination

    def get_queryset(self):
        queryset = Notebook.objects.filter(user=self.request.user)

        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | models.Q(description__icontains=search),
            )

        is_favorite = self.request.query_params.get('is_favorite')
        if is_favorite is not None and is_favorite.lower() in ('true', '1', 'yes'):
            queryset = queryset.filter(is_favorite=True)

        ordering = self.request.query_params.get('ordering', '-updated_at')
        allowed = {'created_at', '-created_at', 'updated_at', '-updated_at', 'name', '-name'}
        if ordering in allowed:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return NotebookCreateSerializer
        if self.action in ('update', 'partial_update'):
            return NotebookUpdateSerializer
        return NotebookSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notebook = serializer.save(user=request.user)
        return Response(
            NotebookSerializer(notebook).data,
            status=201,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        notebook = serializer.save()
        return Response(NotebookSerializer(notebook).data)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        notebook = self.get_object()
        notebook.is_favorite = not notebook.is_favorite
        notebook.save(update_fields=['is_favorite', 'updated_at'])
        return Response(NotebookSerializer(notebook).data)
