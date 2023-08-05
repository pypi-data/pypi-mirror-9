# default values
DEFAULT_REQUEST_TIMEOUT = 60
JSON_RESPONSE_FORMAT = 'json'
DEFAULT_PHONE_LENGTH = 10
DEFAULT_PROFILE_ID_LENGTH = 30
MAX_PLATFORM_USERNAME_LENGTH = 200
DEFAULT_USER_AGENT = 'nextcaller/python/0.0.1'
JSON_CONTENT_TYPE = 'application/json; charset=utf-8'

# urls
DEFAULT_API_VERSION = '2'
BASE_URL = 'https://api.nextcaller.com/v{0}/'
BASE_SANDBOX_URL = 'https://api.sandbox.nextcaller.com/v{0}/'

# address
ADDRESS_MANDATORY_FIELDS = (
    'first_name',
    'last_name',
    'address',
)

ADDRESS_ALLOWED_FIELDS = ADDRESS_MANDATORY_FIELDS + (
    'city',
    'state',
    'zip_code',
    'middle_name',
    'apt_suite',
    'extended_zip',
)
