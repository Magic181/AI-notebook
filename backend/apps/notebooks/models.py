from django.conf import settings
from django.db import models


class Notebook(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notebooks',
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_favorite']),
        ]

    def __str__(self):
        return self.name
