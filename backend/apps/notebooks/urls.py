from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotebookViewSet

router = DefaultRouter()
router.register('notebooks', NotebookViewSet, basename='notebook')

urlpatterns = [
    path('', include(router.urls)),
]
