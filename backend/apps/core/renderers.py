from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    """Wrap all successful responses in { code, message, data } format."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        if isinstance(data, dict) and 'code' in data and 'data' in data:
            return super().render(data, accepted_media_type, renderer_context)

        wrapped = {
            'code': status_code,
            'message': 'success',
            'data': data,
        }
        return super().render(wrapped, accepted_media_type, renderer_context)
