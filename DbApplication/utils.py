from .serializers import *
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin
from django.conf import settings

def getKeycloak():
    config = settings.KEYCLOAK_CONFIG
    keycloak_openid = KeycloakOpenID(server_url = config['KEYCLOAK_SERVER_URL'],
        client_id = config['KEYCLOAK_CLIENT_ID'],
        realm_name = config['KEYCLOAK_REALM'],
        client_secret_key = config['KEYCLOAK_CLIENT_SECRET_KEY'])
    return keycloak_openid

def getKeycloakAdmin():
    config = settings.KEYCLOAK_CONFIG
    print("1",config['KEYCLOAK_SERVER_URL'],"2",
        config['KEYCLOAK_REALM'],"3",
        config['KEYCLOAK_REALM'],"4",
        config['KEYCLOAK_CLIENT_ID'],"5",
        config['KEYCLOAK_CLIENT_SECRET_KEY']
        )
    
    keycloak_connection = KeycloakOpenIDConnection(
        server_url=config['KEYCLOAK_SERVER_URL'],
        realm_name=config['KEYCLOAK_REALM'],
        user_realm_name = config['KEYCLOAK_REALM'],
        client_id = config['KEYCLOAK_CLIENT_ID'],
        client_secret_key = config['KEYCLOAK_CLIENT_SECRET_KEY'],
        verify=True)
    keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
    
    return keycloak_admin