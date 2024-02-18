import logging
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID
from rest_framework import status

logger = logging.getLogger(__name__)

class AuthMiddleware(MiddlewareMixin):
    """
    This middleware is to authorize the users based on JWT. It adds user info to the request that reachs the views.
    """

    def __init__(self, get_response):
        """
        :param get_response:
        """

        self.config = settings.KEYCLOAK_CONFIG

        try:
            self.server_url = self.config['KEYCLOAK_SERVER_URL']
            self.client_id = self.config['KEYCLOAK_CLIENT_ID']
            self.realm = self.config['KEYCLOAK_REALM']
            self.client_secret_key = self.config.get('KEYCLOAK_CLIENT_SECRET_KEY', None)
        except KeyError as e:
            raise Exception("KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID or KEYCLOAK_REALM not found.")

        # Create Keycloak instance
        self.keycloak = KeycloakOpenID(server_url=self.server_url,
                                       client_id=self.client_id,
                                       realm_name=self.realm,
                                       client_secret_key=self.client_secret_key)
        
        self.client_public_key = "-----BEGIN PUBLIC KEY-----\n" + self.keycloak.public_key() + "\n-----END PUBLIC KEY-----"

        # Django
        self.get_response = get_response

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        path = request.path.split('/')[-1]

        if(path in self.config['EXCLUDE_PATH']):
            return None

        # Retrieve the 'Authorization' header from the request
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if(auth_header):
            token = auth_header.split()[1]
            user_response = {
                "username":None,
                "email":None,
                "roles":[]
            }

            try:
                options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
                token_info = self.keycloak.decode_token(token, key=self.client_public_key, options=options)
                logger.debug("token_info ",token_info)
                if "preferred_username" in token_info.keys():
                    user_response["username"] = token_info["preferred_username"]
                # if "email" in token_info.keys():
                #     user_response["email"] = token_info["email"]
            except Exception as e:
                logger.error("Parsing token failed : ",e)
                return JsonResponse({"message": "Invalid token"},status=status.HTTP_401_UNAUTHORIZED)
    
            request.user.details = user_response
            
            request.user.is_active = True
            request.csrf_processing_done = True
            
            
            return None
        else:
            return JsonResponse({"message": "Token not found"},status=status.HTTP_400_BAD_REQUEST)
        