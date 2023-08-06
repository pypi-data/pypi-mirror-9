
import os

try:
    from django.conf import settings
except ImportError:
    settings = None

# Can be overloaded with RPY_DATABASES (instead of using django's db)
DATABASES = settings.DATABASES

# Can be overloaded with RPY_LIB_PATH
LIB_PATH = os.path.join(settings.MEDIA_ROOT, 'rpy', 'libs')

# Can be overloaded with RPY_CRAN_MIRROR
CRAN_MIRROR = "http://cran.us.r-project.org"

# Get all our overloaded settings and all of django's globals
for (name, default) in locals().items():
    locals()[name] = getattr(settings, 'RPY_'+name, default)


