from django.conf import settings
from django.core.checks import Error, Tags, Warning, register


DEV_SECRET_KEY = 'dev-insecure-key'


@register(Tags.security, deploy=True)
def production_settings_check(app_configs, **kwargs):
    if settings.DEBUG:
        return []

    issues = []
    if settings.SECRET_KEY == DEV_SECRET_KEY:
        issues.append(
            Error(
                'DJANGO_SECRET_KEY must be changed when DJANGO_DEBUG=false.',
                hint='Set DJANGO_SECRET_KEY to a strong, private value before deploying.',
                id='core.E001',
            )
        )

    allowed_hosts = set(settings.ALLOWED_HOSTS)
    local_hosts = {'localhost', '127.0.0.1'}
    if not allowed_hosts or allowed_hosts <= local_hosts:
        issues.append(
            Error(
                'DJANGO_ALLOWED_HOSTS must include the production host when DJANGO_DEBUG=false.',
                hint='Set DJANGO_ALLOWED_HOSTS to the comma-separated hostnames served by this deployment.',
                id='core.E002',
            )
        )

    cors_origins = set(getattr(settings, 'CORS_ALLOWED_ORIGINS', []))
    local_origins = {'http://localhost:5173', 'http://127.0.0.1:5173'}
    if not cors_origins or cors_origins <= local_origins:
        issues.append(
            Warning(
                'DJANGO_CORS_ALLOWED_ORIGINS only includes local development origins.',
                hint='Set DJANGO_CORS_ALLOWED_ORIGINS to the frontend origin used in production.',
                id='core.W001',
            )
        )

    return issues
