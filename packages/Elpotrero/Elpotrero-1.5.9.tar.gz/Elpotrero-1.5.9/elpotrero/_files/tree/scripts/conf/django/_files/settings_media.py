import os

from settings_local import BASE_DIR
from settings_local import STATIC_URL
from settings_local import STATIC_ROOT
from settings_local import DEBUG


CRISPY_TEMPLATE_PACK = "uni_form"

MEDIA_BUNDLES = (
    ('projectname.css',
        'css/uni-form/uni-form.css',
        'css/uni-form/default.uni-form.css',
        'css/fonts/chancery.css',
     ),

    ('project.js',
        'js/jquery-1.9.1.js',
        'js/jquery-ui.js',
        'js/jquery.cookie.js',
     ),

)

# Django-MediaGenerator settings

MEDIA_DEV_MODE = DEBUG
DEV_MEDIA_URL = '/devmedia/'
PRODUCTION_MEDIA_URL = '/static/'
GLOBAL_MEDIA_DIRS = (
    os.path.join(BASE_DIR, 'media'),
    os.path.join(BASE_DIR, 'imported-sass-frameworks'),
)

# tinymce settings

TINY_JS_URL = os.path.join(STATIC_URL, 'tiny_mce/tiny_mce.js')
TINY_JS_ROOT = os.path.join(STATIC_ROOT, 'tiny_mce/tiny_mce.js')
TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'relative_urls': False,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}
