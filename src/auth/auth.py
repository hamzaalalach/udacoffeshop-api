import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0

AUTH0_DOMAIN = 'fsndproj.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'drink'
NON_INTERACTIVE_CLIENT_ID = 'BhUMtKF2Of69CYRkhN4ub4Ke0IboP1Cn'
NON_INTERACTIVE_CLIENT_SECRET = 'CqQlpw0ZmCne-'\
    + 'H94mJ6Ju8sD_pInTJA3HfRjO-om7ytJBgX0kpDmnw7soM-XU_h8'

# AuthError Exception


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'missing_auth_header',
            'description': 'Authorization header is required.'
        }, 401)

    parts = auth.split(' ')
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with Bearer.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be a Bearer token.'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    return parts[1]


def check_permissions(permissions, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not found in JWT.'
        }, 400)
    # Get all permissions in the string
    parts = permissions.split(', ')
    matched_perms = []
    found = False

    # check if at least one of them exists
    for permission in parts:
        if permission in payload['permissions']:
            matched_perms.append(permission)
            found = True
    # If not raise 401
    if not found:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)
    # If found return it
    else:
        return matched_perms


def verify_decode_jwt(token):
    jwks = json.loads(
        urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json').read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims.\
                    Please, check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except BaseException:
                abort(401)

            # Check if at least one permission exists
            result = check_permissions(permission, payload)
            manaj_perms = []
            if result:
                for perm in result:
                    # Check if manage permissions are in use
                    if 'manage' in perm:
                        manaj_perms.append(perm.split(':')[1])
            # If manage permission, add it as first argument
            if len(manaj_perms):
                return f(manaj_perms, *args, **kwargs)
            else:
                return f(*args, **kwargs)

        return wrapper
    return requires_auth_decorator


def get_mgmt_token():
    get_token = GetToken(AUTH0_DOMAIN)
    token = get_token.client_credentials(
        NON_INTERACTIVE_CLIENT_ID,
        NON_INTERACTIVE_CLIENT_SECRET,
        'https://{}/api/v2/'.format(AUTH0_DOMAIN))

    return token['access_token']


def init_mgmt():
    return Auth0(AUTH0_DOMAIN, get_mgmt_token())
