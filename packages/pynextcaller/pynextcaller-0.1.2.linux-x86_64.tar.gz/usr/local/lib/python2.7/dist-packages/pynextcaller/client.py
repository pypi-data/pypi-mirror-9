from __future__ import unicode_literals
from .auth import *
from .constants import *
from .utils import *
from .transport import make_http_request


class NextCallerClient(object):
    """The NextCaller API client"""

    def __init__(self, username, password, version=DEFAULT_API_VERSION,
                 sandbox=False, debug=False):
        """
        Initialize NextCaller client with API username
        and password for Basic Authorization

        :param username:str     API username
        :param password:str     API password
        :param version:str      API version
        :param sandbox:bool     If True - sandbox mode is turned on
        :param debug:bool       If True - all actions will be reflected
                                in console output
        """
        self.auth = BasicAuth(username, password)
        self.sandbox = bool(sandbox)
        self.base_url = prepare_base_url(sandbox, version)
        self.debug = debug

    @check_kwargs
    def get_by_phone(self, phone, **kwargs):
        """
        Get profile by a phone number

        :param phone:str    10 digit phone number
        :param kwargs:dict  Additional params for request

        :return:list        Serialised response as list
        """
        validate_phone(phone)
        url_params = dict({
            'phone': phone,
            'format': JSON_RESPONSE_FORMAT,
        }, **kwargs)
        url = prepare_url(self.base_url, 'records/', url_params=url_params)
        response = make_http_request(
            self.auth, url, method='GET', debug=self.debug)
        return default_handle_response(response)

    @check_kwargs
    def get_by_profile_id(self, profile_id, **kwargs):
        """
        Get profile by a profile id

        :param profile_id:str   Profile identifier from get_by_phone
                                response with length in 30 symbols
        :param kwargs:dict      Additional params for request

        :return:dict            Serialised response as dictionary
        """
        validate_profile_id(profile_id)
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **kwargs)
        url = prepare_url(self.base_url, 'users/{0}/'.format(profile_id),
                          url_params=url_params)
        response = make_http_request(
            self.auth, url, method='GET', debug=self.debug)
        return default_handle_response(response)

    @check_kwargs
    def get_by_address_name(self, data, **kwargs):
        """
        Get profile by an address

        :param data:dict        Profile identifier from get_by_phone
                                response with length in 30 symbols
        :param kwargs:dict      Additional params for request

        :return:dict            Serialised response as dictionary
        """
        clean_data = validate_address(data)
        clean_data.update(kwargs)
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **clean_data)
        url = prepare_url(self.base_url, 'records/', url_params=url_params)
        response = make_http_request(
            self.auth, url, method='GET', debug=self.debug)
        return default_handle_response(response)

    @check_kwargs
    def update_by_profile_id(self, profile_id, data, **kwargs):
        """
        Update profile by a profile id

        :param profile_id:str   Profile identifier from get_by_phone
                                response with length in 30 symbols
        :param data:dict        Data to update as dictionary
        :param kwargs:dict      Additional params for request

        :return:str             HTTP Body of response as text
        """
        validate_profile_id(profile_id)
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **kwargs)
        url = prepare_url(self.base_url, 'users/{0}/'.format(profile_id),
                          url_params=url_params)
        data = prepare_json_data(data)
        return make_http_request(
            self.auth, url, data=data, method='POST',
            content_type=JSON_CONTENT_TYPE, debug=self.debug
        )

    @check_kwargs
    def get_fraud_level(self, phone, **kwargs):
        """
        Get fraud level for a phone number

        :param phone:str    10 digit phone number
        :param kwargs:dict  Additional params for request

        :return:dict        Serialised response as dictionary
        """
        validate_phone(phone)
        url_params = dict({
            'phone': phone,
            'format': JSON_RESPONSE_FORMAT,
        }, **kwargs)
        url = prepare_url(self.base_url, 'fraud/', url_params=url_params)
        response = make_http_request(
            self.auth, url, method='GET', debug=self.debug)
        return default_handle_response(response)


class NextCallerPlatformClient(NextCallerClient):
    """The NextCaller platform API client"""

    @check_kwargs
    def get_by_phone(self, phone, platform_username, **kwargs):
        """
        Get profile by a phone number

        :param phone:str                10 digit phone number
        :param platform_username:str    Name of platform user
        :param kwargs:dict              Additional params for request

        :return:list                    Serialised response as list
        """
        validate_platform_username(platform_username)
        return super(NextCallerPlatformClient, self).get_by_phone(
            phone, platform_username=platform_username, **kwargs
        )

    @check_kwargs
    def get_by_profile_id(self, profile_id, platform_username, **kwargs):
        """
        Get profile by a profile id

        :param profile_id:str           Profile identifier from get_by_phone
                                        response with length in 30 symbols
        :param platform_username:str    Name of platform user
        :param kwargs:dict              Additional params for request

        :return:dict                    Serialised response as dictionary
        """
        validate_platform_username(platform_username)
        return super(NextCallerPlatformClient, self).get_by_profile_id(
            profile_id, platform_username=platform_username, **kwargs
        )

    @check_kwargs
    def get_by_address_name(self, data, platform_username, **kwargs):
        """
        Get profile by an address

        :param data:dict                Profile identifier from get_by_phone
                                        response with length in 30 symbols
        :param platform_username:str    Name of platform user
        :param kwargs:dict              Additional params for request

        :return:dict                    Serialised response as dictionary
        """
        validate_platform_username(platform_username)
        return super(NextCallerPlatformClient, self).get_by_address_name(
            data, platform_username=platform_username, **kwargs
        )

    @check_kwargs
    def update_by_profile_id(self, profile_id, data,
                             platform_username, **kwargs):
        """
        Update profile by a profile id

        :param profile_id:str           Profile identifier from get_by_phone
                                        response with length in 30 symbols
        :param data:dict                Data to update as dictionary
        :param platform_username:str    Name of platform user
        :param kwargs:dict              Additional params for request

        :return:str                     HTTP Body of response as text
        """
        validate_platform_username(platform_username)
        return super(NextCallerPlatformClient, self).update_by_profile_id(
            profile_id, data, platform_username=platform_username, **kwargs
        )

    def get_platform_statistics(self, page=1, **kwargs):
        """
        Get platform statistics as dictionary
        with list of platform users

        :param page:int     Number of page with users
        :param kwargs:dict  Additional params for request

        :return:dict        Dictionary with platform statistic
        """
        url_params = dict({
            'page': page,
            'format': JSON_RESPONSE_FORMAT,
        }, **kwargs)
        url = prepare_url(
            self.base_url, 'platform_users/', url_params=url_params)
        response = make_http_request(
            self.auth, url, method='GET', debug=self.debug)
        return default_handle_response(response)

    def get_platform_user(self, platform_username, **kwargs):
        """
        Get platform user detail data by platform username

        :param platform_username:str   Name of platform user

        :return:dict                   Platform user detail data
        """
        validate_platform_username(platform_username)
        url_params = dict({
            'format': JSON_RESPONSE_FORMAT
        }, **kwargs)
        url_path = 'platform_users/{0}/'.format(platform_username)
        url = prepare_url(self.base_url, url_path, url_params=url_params)
        response = make_http_request(
            self.auth, url, method='GET', debug=self.debug)
        return default_handle_response(response)

    def update_platform_user(self, platform_username, data):
        """
        Update platform user data

        :param platform_username:str    Name of platform user
        :param data:dict                Data to update as dictionary

        :return:str                     HTTP Body of response as text
        """
        validate_platform_username(platform_username)
        url_params = {
            'format': JSON_RESPONSE_FORMAT
        }
        url = prepare_url(
            self.base_url, 'platform_users/{0}/'.format(platform_username),
            url_params=url_params)
        data = prepare_json_data(data)
        return make_http_request(
            self.auth, url, data=data, method='POST',
            content_type=JSON_CONTENT_TYPE, debug=self.debug
        )

    def get_fraud_level(self, phone, platform_username, **kwargs):
        """
        Get fraud level for a phone

        :param phone:str                10 digit phone number
        :param platform_username:str    Name of platform user
        :param kwargs:dict              Additional params for request

        :return:dict                    Serialised response as dictionary
        """
        validate_platform_username(platform_username)
        return super(NextCallerPlatformClient, self).get_fraud_level(
            phone, platform_username=platform_username, **kwargs
        )
