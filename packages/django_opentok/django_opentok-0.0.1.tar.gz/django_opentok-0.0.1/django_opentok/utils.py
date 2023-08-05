from opentok import OpenTok, MediaModes

from django.conf import settings
 

def create_session():
    api_key = settings.OPENTOK_API_KEY
    api_secret = settings.OPENTOK_SECRET_KEY
     
    opentok_sdk = OpenTok(api_key, api_secret)
    session = opentok_sdk.create_session(media_mode=MediaModes.routed)

    return session.session_id


def generate_token(session_id):
    api_key = settings.OPENTOK_API_KEY
    api_secret = settings.OPENTOK_SECRET_KEY
     
    opentok_sdk = OpenTok(api_key, api_secret)
    token = opentok_sdk.generate_token(session_id=session_id)

    return token
