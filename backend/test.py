import requests
import jwt
from jwt.algorithms import RSAAlgorithm
from google.auth.transport import requests as google_requests

# The credential JWT from Google OAuth2 response
credential_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjMxYjhmY2NiMmU1MjI1M2IxMzMxMzhhY2YwZTU2NjMyZjA5OTU3ZWUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0NTQyMjA4Nzk0NTgtM2Z2bzI2aDJqcWVzYzM2aHJjNHQyZ2FzaXIyZnZwdDEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0NTQyMjA4Nzk0NTgtM2Z2bzI2aDJqcWVzYzM2aHJjNHQyZ2FzaXIyZnZwdDEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTEzNzg0MDA2MTcxOTg0NDUyNzUiLCJlbWFpbCI6ImdyZWVuc2xpbWUxMDI0QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYmYiOjE3MzUyMDE4MzIsIm5hbWUiOiJHcmVlblNsaW1lMTAyNCIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMa0Y0UUtNV3p4ZnlOc2VycmRIa3lfMDdJTlFQY3NGZVlYV0NfNm8waXNFc1p0ZHZWND1zOTYtYyIsImdpdmVuX25hbWUiOiJHcmVlblNsaW1lMTAyNCIsImlhdCI6MTczNTIwMjEzMiwiZXhwIjoxNzM1MjA1NzMyLCJqdGkiOiI5MmZmODU3YTgzYThlMjMyYzM1MGY4NDU0ZjcyYWY5OTMxYjJiNmFkIn0.YQyzghd7iswSWE_NnzkC9EiEFOV8x4Dqeshr7fLKeBxMEshayagnPiRNuTFA9_q-_yx911uYuR2n5Iy0I2bzlEYZTQSbt4Kjk2x-rfC32CbMUwh69Yov8vFK5V1XOPfsTdd4B3f_4kgOND85tWmcxLl8gWz3CPLNe-AKOL5RANpsJzhalO7J58398Q4rkcsY4-liNw3SmMGRfmd3tWo9pRYU5-RSZDtQKD9TQZPfHEN6DR2VTmfHq5YMEL5i0UEvYSyLfM8Kav92Kzqag4kJZTCMu0dPugQ3wW4IcDOnPc8-ssMjh2XI_ce-UBcoJPROzgpKBCMf7I65sdFsUG57Mg'

# Fetch Google's public keys to verify the JWT
public_keys_url = "https://www.googleapis.com/oauth2/v3/certs"
response = requests.get(public_keys_url)
public_keys = response.json()

# Decode and verify the JWT
def verify_google_jwt(token):
    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        
        if unverified_header.get("kid"):
            for key in public_keys['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
        
        if rsa_key:
            # Verify the token using the public key
            payload = jwt.decode(
                token,
                RSAAlgorithm.from_jwk(rsa_key),
                algorithms=['RS256'],
                audience='454220879458-3fvo26h2jqesc36hrc4t2gasir2fvpt1.apps.googleusercontent.com',
                issuer='https://accounts.google.com'
            )
            return payload
        else:
            raise ValueError("Unable to find appropriate key.")
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
    except jwt.JWTClaimsError:
        print("Invalid claims.")
    except Exception as e:
        print(f"Error verifying JWT: {e}")

# Call the function to verify and decode the JWT
user_info = verify_google_jwt(credential_token)

if user_info:
    print("User Info:", user_info)
else:
    print("Invalid or expired JWT.")
