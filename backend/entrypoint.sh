#!/usr/bin/env sh
set -eu

if [ "${SKIP_MIGRATIONS:-false}" != "true" ]; then
  python manage.py migrate --noinput
fi

if [ "${SKIP_COLLECTSTATIC:-false}" != "true" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"
