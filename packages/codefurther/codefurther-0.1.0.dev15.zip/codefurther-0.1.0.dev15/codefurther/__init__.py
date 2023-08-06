import os
from appdirs import user_data_dir
from codefurther.helpers import Config, KNOWN_SETTINGS

__author__ = 'Danny Goodall'
__version__ = "0.1.0.dev1"
appname = "codefurther"
appauthor = "codefurther"
conf_dir = user_data_dir(appname, appauthor)
settings_file = "cf_settings.py"

settings_location=None
# Look for the cf_settings.py file
locations = [os.environ.get("CF_CONF_DIR")]
if locations[0] is None:
    locations =[os.curdir, conf_dir, '..']
else:
    locations.extend[os.curdir, conf_dir, '..']

for location in locations:
    file_location = os.path.join(location, settings_file)
    if os.path.isfile(file_location):
        settings_location = file_location
        break


# Create a config variable
cf_config = Config('')

# Grab the config from a cf_settings.py file - if it's there
if settings_location is not None:
    cf_config.from_pyfile(settings_location, silent=True)

# Now grab config from the environment
cf_config.from_envvars(KNOWN_SETTINGS, silent=True)

