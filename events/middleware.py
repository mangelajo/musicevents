from django.middleware.csrf import CsrfViewMiddleware

class CustomCsrfMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Exempt admin login from CSRF protection
        if request.path.startswith('/admin/login/'):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)