from django.conf import settings


def opentok(request):
    api_key = settings.OPENTOK_API_KEY

    context_dict = { 
        'opentok_api_key': api_key,
    }
    
    return context_dict
