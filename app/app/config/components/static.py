"""Static files (CSS, JavaScript, Images)."""
import os

STATIC_URL = '/static/'
STATIC_ROOT = os.path.dirname(
    os.path.abspath(__file__) + '/../../static/',
)
MEDIA_URL = '/media/'
