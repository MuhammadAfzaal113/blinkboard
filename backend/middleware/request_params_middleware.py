from ..models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class AccessTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if 'access_token' is present in query parameters
        access_token = request.GET.get('access_token', None)

        if access_token:
            try:
                decoded_token = AccessToken(access_token)
                # Decode the access token and get the associated user
                user = User.objects.get(id=decoded_token['user_id'])
                request.user = user  # Attach the user to the request
            except ObjectDoesNotExist:
                # Handle the case where the user is not found
                pass
        response = self.get_response(request)
        return response

    def decode_access_token(self, access_token):
        # Implement your logic to decode the access token here
        # This might involve using a library like PyJWT or Django's built-in tools
        # For simplicity, let's assume the access token is the username for now
        return access_token
