from facebookads import FacebookSession, FacebookAdsApi
from facebookads.objects import (
    AdAccount,
    AdSet,
    AdGroup,
    AdCampaign,
    CustomAudience,
    AdConversionPixel,
    AdImage
)

from facebookadmanager import utils

CREATE = u'CREATE'
READ = u'READ'
UPDATE = u'UPDATE'
DELETE = u'DELETE'


MAX_BATCH_SIZE = 50


class FacebookAPIClient(object):
    """
    This class supplies a connection to the Facebook Ads API and methods for interacting with it given local objects.
    """

    def __init__(self, app_id, app_secret, access_token, logger=None):
        """
        Instantiate the client but don't connect to Facebook

        Args:
            app_id (str): The identifier for the app associated with admin account
            app_secret (str): The secret code associated with the app
            access_token (str): OAuth token string used to authenticate the admin user
            logger (logger instance, optional): The logger used during operation, default facebookadmanager.utils.logger
        """

        self.logger = logger if logger else utils.logger

        self.last_batch_results = []

        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token

    def connect(self):
        """
        Retrieve an admin user account from provided keys, create
        FacebookSession, FacebookAdsApi instance, and assign the admin user
        account.

        Args:
            None

        Returns:
            None
        """

        session = FacebookSession(self.app_id, self.app_secret, self.access_token)

        api = FacebookAdsApi(session)

        FacebookAdsApi.set_default_api(api)

        self.account = AdAccount.get_my_account()

    def local_object_to_remote_object(self, local_object):
        """
        Maps an AdRoll Facebook MirrorObject to a facebookads object and populates it with MirrorObject.dict which
        is should be the mapping of fields designated by Facebook's API

        Args:
            local_object : a FacebookBase object
            method (str): the CRUD method being used in the request, used to marshall the local_object to proper format

        Return:
            a facebookads.AbstractCrudObject
        """

        account_id = 'act_{}'.format(local_object.account_id)
        remote_object = local_object.remote_object_class(parent_id=account_id)

        if hasattr(local_object, 'get_read_fields'):
            read_fields = local_object.get_read_fields()
        else:
            read_fields = ['id']

        remote_object.set_default_read_fields(read_fields)

        return remote_object

    def get_new_batch(self):
        return self.account.get_api_assured().new_batch()

    #--------------------#
    # Basic CRUD Methods #
    #--------------------#

    def _execute(self, method, local_object, batch=None):
        """
        Operate on a single facebookads AbstractCRUD object or add an operation to a given batch to execute later.

        Args:
            method: a string denoting the type of request to make to the Facebook API
            local_object: a FacebookBase object that implements a function named `remote_{method}`
            batch (optional): A FacebookAdsApiBatch object, default None for immediate execution of request
        """
        remote_object = self.local_object_to_remote_object(local_object)
        data = local_object.get_marshalled_data(method)
        remote_object.update(data)


        success = local_object.success_callback(method, remote_object=remote_object)
        failure = local_object.failure_callback(method, remote_object=remote_object)

        method_name = 'remote_{}'.format(method.lower())
        remote_function = getattr(remote_object, method_name)

        self.logger.warning('{}: {}'.format(method, remote_object))

        remote_function(
            batch=batch,
            success=success,
            failure=failure
        )

    def create(self, local_object, batch=None):
        """
        Create a single facebookads AbstractCRUD object with or add a call for creation to a given batch to be
        executed later.

        Args:
            local_object: a FacebookBase object
            batch (optional): A FacebookAdsApiBatch object, default None for immediate execution of request
        """
        self._execute(
            CREATE,
            local_object,
            batch=batch
        )

    def read(self, local_object, batch=None):
        """
        Read a single facebookads AbstractCRUD object with or add a call for reading to a given batch to be
        executed later.

        Args:
            local_object: a FacebookBase object
            batch (optional): A FacebookAdsApiBatch object, default None for immediate execution of request
        """
        self._execute(
            READ,
            local_object,
            batch=batch
        )

    def update(self, local_object, batch=None):
        """
        Update a single facebookads AbstractCRUD object with or add a call for updating to a given batch to be
        executed later.

        Args:
            local_object: a FacebookBase object
            batch (optional): A FacebookAdsApiBatch object, default None for immediate execution of request
        """

        self._execute(
            UPDATE,
            local_object,
            batch=batch
        )

    def delete(self, local_object, batch=None):
        """
        Delete a single facebookads AbstractCRUD object with or add a call for deletion to a given batch to be
        executed later.

        Args:
            local_object: a FacebookBase object
            batch (optional): A FacebookAdsApiBatch object, default None for immediate execution of request
        """
        self._execute(
            DELETE,
            local_object,
            batch=batch
        )

    #--------------------#
    # Batch CRUD Methods #
    #--------------------#

    def _execute_batch(self, method, local_objects):
        """
        Creates a list of FacebookBase objects remotely through a corresponding AbstractCrudObject and the Facebook API

        Args:
            local_objects (list of FacebookBase objects): list of local objects to sync remotely
        """

        if not local_objects:
            return

        batch = self.get_new_batch()

        crud_function = getattr(self, method.lower())

        for local_object in local_objects:
            crud_function(local_object, batch=batch)

        batch.execute()

    def create_batch(self, local_objects):
        """
        Creates a list of FacebookBase objects remotely through a corresponding AbstractCrudObject and the Facebook API

        Args:
            local_objects (list of FacebookBase objects): list of local objects to sync remotely
        """

        self._execute_batch(CREATE, local_objects)

    def read_batch(self, local_objects):
        """
        Creates a list of FacebookBase objects remotely through a corresponding AbstractCrudObject and the Facebook API

        Args:
            local_objects (list of FacebookBase objects): list of local objects to sync remotely
        """

        self._execute_batch(READ, local_objects)

    def update_batch(self, local_objects):
        """
        Creates a list of FacebookBase objects remotely through a corresponding AbstractCrudObject and the Facebook API

        Args:
            local_objects (list of FacebookBase objects): list of local objects to sync remotely
        """

        self._execute_batch(UPDATE, local_objects)

    def delete_batch(self, local_objects):
        """
        Creates a list of FacebookBase objects remotely through a corresponding AbstractCrudObject and the Facebook API

        Args:
            local_objects (list of FacebookBase objects): list of local objects to sync remotely
        """

        self._execute_batch(DELETE, local_objects)

    #-----------------------#
    # Campaign CRUD Methods #
    #-----------------------#

    def create_campaigns(self, facebook_campaigns):
        """
        Creates a list of FacebookCampaigns remotely through a corresponding AdCampaign and the Facebook API

        Args:
            facebook_campaigns (list of FacebookCampaigns): list of local objects to sync remotely
        """

        self.create_batch(facebook_campaigns)

    def read_campaigns(self, facebook_campaigns):
        """
        Reads a list of FacebookCampaigns remotely through a corresponding AdCampaign and the Facebook API

        Args:
            facebook_campaigns (list of FacebookCampaign):

        """

        self.read_batch(facebook_campaigns)

    def update_campaigns(self, facebook_campaigns):
        """
        Updates a list of FacebookCampaigns remotely through a corresponding AdCampaign and the Facebook API

        Args:
            facebook_campaigns (list of FacebookCampaign):

        """

        self.update_batch(facebook_campaigns)

    def delete_campaigns(self, facebook_campaigns):
        """
        Deletes a list of FacebookCampaigns remotely through a corresponding AdCampaign and the Facebook API

        Args:
            facebook_campaigns (list of FacebookCampaign):

        """

        self.delete_batch(facebook_campaigns)

    #--------------------#
    # AdSet CRUD Methods #
    #--------------------#

    def create_adsets(self, facebook_adsets):
        """
        Creates a list of FacebookAdSets remotely through a corresponding AdSet and the Facebook API

        Args:
            facebook_adsets (list of FacebookAdSets): list of local objects to sync remotely
        """

        self.create_batch(facebook_adsets)

    def read_adsets(self, facebook_adsets):
        """
        Reads a list of FacebookAdSets remotely through a corresponding AdSet and the Facebook API

        Args:
            facebook_adsets (list of FacebookAdSet):

        """

        self.read_batch(facebook_adsets)

    def update_adsets(self, facebook_adsets):
        """
        Updates a list of FacebookAdSets remotely through a corresponding AdSet and the Facebook API

        Args:
            facebook_adsets (list of FacebookAdSet):

        """

        self.update_batch(facebook_adsets)

    def delete_adsets(self, facebook_adsets):
        """
        Deletes a list of FacebookAdSets remotely through a corresponding AdSet and the Facebook API

        Args:
            facebook_adsets (list of FacebookAdSet):

        """

        self.delete_batch(facebook_adsets)

    #----------------------#
    # AdGroup CRUD Methods #
    #----------------------#

    def create_adgroups(self, facebook_adgroups):
        """
        Creates a list of FacebookAdGroups remotely through a corresponding AdGroup and the Facebook API

        Args:
            facebook_adgroups (list of FacebookAdGroups): list of local objects to sync remotely
        """

        self.create_batch(facebook_adgroups)

    def read_adgroups(self, facebook_adgroups):
        """
        Reads a list of FacebookAdGroups remotely through a corresponding AdGroup and the Facebook API

        Args:
            facebook_adgroups (list of FacebookAdGroup):

        """

        self.read_batch(facebook_adgroups)

    def update_adgroups(self, facebook_adgroups):
        """
        Updates a list of FacebookAdGroups remotely through a corresponding AdGroup and the Facebook API

        Args:
            facebook_adgroups (list of FacebookAdGroup):

        """

        self.update_batch(facebook_adgroups)

    def delete_adgroups(self, facebook_adgroups):
        """
        Deletes a list of FacebookAdGroups remotely through a corresponding AdGroup and the Facebook API

        Args:
            facebook_adgroups (list of FacebookAdGroup):

        """

        self.delete_batch(facebook_adgroups)

    #-----------------------------#
    # CustomAudience CRUD Methods #
    #-----------------------------#

    def create_custom_audiences(self, facebook_custom_audiences):
        """
        Creates a list of FacebookCustomAudiences remotely through a corresponding CustomAudience and the Facebook API

        Args:
            facebook_custom_audiences (list of FacebookCustomAudiences): list of local objects to sync remotely
        """

        self.create_batch(facebook_custom_audiences)

    def read_custom_audiences(self, facebook_custom_audiences):
        """
        Reads a list of FacebookCustomAudiences remotely through a corresponding CustomAudience and the Facebook API

        Args:
            facebook_custom_audiences (list of FacebookCustomAudience):

        """

        self.read_batch(facebook_custom_audiences)

    def update_custom_audiences(self, facebook_custom_audiences):
        """
        Updates a list of FacebookCustomAudiences remotely through a corresponding CustomAudience and the Facebook API

        Args:
            facebook_custom_audiences (list of FacebookCustomAudience):

        """

        self.update_batch(facebook_custom_audiences)

    def delete_custom_audiences(self, facebook_custom_audiences):
        """
        Deletes a list of FacebookCustomAudiences remotely through a corresponding CustomAudience and the Facebook API

        Args:
            facebook_custom_audiences (list of FacebookCustomAudience):

        """

        self.delete_batch(facebook_custom_audiences)

    #--------------------------------#
    # Special CustomAudience Methods #
    #--------------------------------#

    def add_users_to_custom_audience(self, facebook_custom_audience):
        """
        Adds users to a custom audience based on the hashed user list and schema provided by the object itself

        Args:
            facebook_custom_audience (FacebookCustomAudience): local instance of FacebookCustomAudience

        """
        remote_object = self.local_object_to_remote_object(facebook_custom_audience)
        data = {
            u'id': facebook_custom_audience.external_id,
        }
        remote_object.update(data)
        remote_object.add_users(facebook_custom_audience.schema, facebook_custom_audience.users)

    def remove_users_from_custom_audience(self, facebook_custom_audience):
        """
        Removes users to a custom audience based on the hashed user list and schema provided by the object itself

        Args:
            facebook_custom_audience (FacebookCustomAudience): local instance of FacebookCustomAudience

        """
        remote_object = self.local_object_to_remote_object(facebook_custom_audience)
        data = {
            u'id': facebook_custom_audience.external_id,
        }
        remote_object.update(data)
        remote_object.remove_users(facebook_custom_audience.schema, facebook_custom_audience.users)

    #--------------------------------#
    # AdConversionPixel CRUD Methods #
    #--------------------------------#

    def create_ad_conversion_pixels(self, facebook_ad_conversion_pixels):
        """
        Creates a list of FacebookAdConversionPixels remotely through a corresponding AdConversionPixel and the Facebook API

        Args:
            facebook_ad_conversion_pixels (list of FacebookAdConversionPixels): list of local objects to sync remotely
        """

        self.create_batch(facebook_ad_conversion_pixels)

    def read_ad_conversion_pixels(self, facebook_ad_conversion_pixels):
        """
        Reads a list of FacebookAdConversionPixels remotely through a corresponding AdConversionPixel and the Facebook API

        Args:
            facebook_ad_conversion_pixels (list of FacebookAdConversionPixel):

        """

        self.read_batch(facebook_ad_conversion_pixels)

    def update_ad_conversion_pixels(self, facebook_ad_conversion_pixels):
        """
        Updates a list of FacebookAdConversionPixels remotely through a corresponding AdConversionPixel and the Facebook API

        Args:
            facebook_ad_conversion_pixels (list of FacebookAdConversionPixel):

        """

        self.update_batch(facebook_ad_conversion_pixels)

    def delete_ad_conversion_pixels(self, facebook_ad_conversion_pixels):
        """
        Deletes a list of FacebookAdConversionPixels remotely through a corresponding AdConversionPixel and the Facebook API

        Args:
            facebook_ad_conversion_pixels (list of FacebookAdConversionPixel):

        """

        self.delete_batch(facebook_ad_conversion_pixels)

    #----------------------#
    # AdImage CRUD Methods #
    #----------------------#

    def create_ad_images(self, facebook_ad_images):
        """
        Creates a list of FacebookAdImages remotely through a corresponding AdCampaign and the Facebook API

        Args:
            facebook_ad_images (list of FacebookAdImages): list of local objects to sync remotely
        """

        self.create_batch(facebook_ad_images)

    def read_ad_images(self, facebook_ad_images):
        """
        Reads a list of FacebookAdImages remotely through a corresponding AdImage and the Facebook API

        Args:
            facebook_ad_images (list of FacebookAdImage):

        """

        self.read_batch(facebook_ad_images)

    def update_ad_images(self, facebook_ad_images):
        """
        Updates a list of FacebookAdImages remotely through a corresponding AdCampaign and the Facebook API

        Args:
            facebook_ad_images (list of FacebookAdImage):

        """

        self.update_batch(facebook_ad_images)

    def delete_ad_images(self, facebook_ad_images):
        """
        Deletes a list of FacebookAdImages remotely through a corresponding AdCampaign and the Facebook API

        Args:
            facebook_ad_images (list of FacebookAdImage):

        """

        self.delete_batch(facebook_ad_images)
