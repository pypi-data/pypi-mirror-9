from django.conf import settings

VERNISSAGE_GALLERY_ATTRIBUTES = getattr(
    settings, 'VERNISSAGE_GALLERY_ATTRIBUTES', {
        "data-interval": 5000,
        "data-pause": "hover",
        "data-wrap": True,
        "data-keyboard": True,
    })

VERNISSAGE_ADMIN = getattr(settings, 'VERNISSAGE_ADMIN', True)
