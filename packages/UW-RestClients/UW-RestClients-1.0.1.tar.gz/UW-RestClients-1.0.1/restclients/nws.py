"""
This is the interface for interacting with the Notifications Web Service.
"""

import re
import json
from restclients.dao import NWS_DAO
from restclients.exceptions import DataFailureException, InvalidUUID, InvalidNetID, InvalidEndpointProtocol, InvalidRegID
from restclients.models import CourseAvailableEvent
from urllib import quote
from datetime import datetime, time
from vm.v1.viewmodels import Channel, ChannelList, Endpoint, EndpointList, Serializer, Subscription, SubscriptionList
from vm.v1.viewmodels import Person, PersonList
from restclients.sws.term import get_current_term, get_term_after


MANAGED_ATTRIBUTES = ('DispatchedEmailCount', 'DispatchedTextMessageCount', 'SentTextMessageCount', 'SubscriptionCount')

class NWS(object):
    """
    The NWS object has methods for getting, updating, deleting information
    about channels, subscriptions, endpoints, and templates.
    """

    def __init__(self, override_user = None):
        self.override_user = override_user

    #ENDPOINT RESOURCE
    def get_endpoints(self, first_result = 1, max_results = 10):
        """
        Search for all endpoints
        """
        url = "/notification/v1/endpoint?first_result=%s&max_results=%s" % (first_result, max_results)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        endpoint_list = EndpointList()
        Serializer().deserialize(endpoint_list, response.data)

        return endpoint_list.view_models

    def get_endpoint_by_endpoint_id(self, endpoint_id):
        """
        Get an endpoint by endpoint id
        """
        #Validate the channel_id
        self._validate_uuid(endpoint_id)

        url = "/notification/v1/endpoint/%s" % (endpoint_id)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        endpoint = Endpoint()
        Serializer().deserialize(endpoint, response.data)

        return endpoint

        #return self._endpoint_from_json(json.loads(response.data))

    def get_endpoint_by_subscriber_id_and_protocol(self, subscriber_id, protocol):
        """
        Get an endpoint by subscriber_id and protocol
        """
        self._validate_subscriber_id(subscriber_id)

        url = "/notification/v1/endpoint?subscriber_id=%s&protocol=%s" % (subscriber_id, protocol)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        endpoint_list = EndpointList()
        Serializer().deserialize(endpoint_list, response.data)

        endpoint_vms = endpoint_list.view_models
        if len(endpoint_vms) == 0:
            raise DataFailureException(url, 404, {"Message": "No SMS endpoint found"})

        endpoint = endpoint_vms[0]
        return endpoint

    def get_endpoint_by_address(self, endpoint_address):
        """
        Get an endpoint by address
        """

        url = "/notification/v1/endpoint?endpoint_address=%s" % endpoint_address

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:

            raise DataFailureException(url, response.status, response.data)

        endpoint_list = EndpointList()
        Serializer().deserialize(endpoint_list, response.data)

        endpoint_vms = endpoint_list.view_models
        if len(endpoint_vms) == 0:
            raise DataFailureException(url, 404, {"Message": "No endpoint found"})

        endpoint = endpoint_vms[0]
        return endpoint

    def get_endpoints_by_subscriber_id(self, subscriber_id):
        """
        Search for all endpoints by a given subscriber
        """
        #Validate input
        self._validate_subscriber_id(subscriber_id)

        url = "/notification/v1/endpoint?subscriber_id=%s" % (subscriber_id)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        endpoint_list = EndpointList()
        Serializer().deserialize(endpoint_list, response.data)

        return endpoint_list.view_models

    def resend_sms_endpoint_verification(self, endpoint_id):
        """
        Calls NWS function to resend verification message to endpoint's phone number
        """
        #Validate input
        self._validate_uuid(endpoint_id)

        url = "/notification/v1/endpoint/%s/verification" % (endpoint_id)

        dao = NWS_DAO()
        post_response = dao.postURL(url, None, None)

        if post_response.status != 202:
            raise DataFailureException(url, post_response.status, post_response.data)

        return post_response.status

    def delete_endpoint(self, endpoint_id):
        """
        Deleting an existing endpoint

        :param endpoint_id:
        is the endpoint that the client wants to delete
        """

        #Validate the subscription_id
        self._validate_uuid(endpoint_id)

        #Delete the subscription
        url = "/notification/v1/endpoint/%s" % (endpoint_id)
        headers = {}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user
        dao = NWS_DAO()
        delete_response = dao.deleteURL(url, headers)

        #Http response code 204 No Content:
        #The server has fulfilled the request but does not need to return an entity-body
        if delete_response.status != 204:
            raise DataFailureException(url, delete_response.status, delete_response.data)

        return delete_response.status

    def update_endpoint(self, endpoint):
        """
        Update an existing endpoint

        :param endpoint:
        is the updated endpoint that the client wants to update
        """
        #Validate
        self._validate_uuid(endpoint.endpoint_id)
        self._validate_subscriber_id(endpoint.user)

        #Update the subscription
        dao = NWS_DAO()
        url = "/notification/v1/endpoint/%s" % (endpoint.endpoint_id)
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        put_response = dao.putURL(url, headers, Serializer().serialize(endpoint))

        #Http response code 204 No Content:
        #The server has fulfilled the request but does not need to return an entity-body
        if put_response.status != 204:
            raise DataFailureException(url, put_response.status, put_response.data)

        return put_response.status

    def create_new_endpoint(self, endpoint):
        """
        Create a new endpoint

        :param endpoint:
        is the new endpoint that the client wants to create
        """
        #Validate
        self._validate_subscriber_id(endpoint.get_user_net_id())

        #Create new subscription
        dao = NWS_DAO()
        url = "/notification/v1/endpoint"
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        post_response = dao.postURL(url, headers, Serializer().serialize(endpoint))

        #HTTP Status Code 201 Created: The request has been fulfilled and resulted
        #in a new resource being created
        if post_response.status != 201:
            raise DataFailureException(url, post_response.status, post_response.data)

        return post_response.status


    #PERSON RESOURCE
    def create_new_person(self, person):
        """
        Create a new person

        :param person:
        is the new person that the client wants to crete
        """
        #Validate input
        self._validate_subscriber_id(person.surrogate_id)

        #Create new person
        dao = NWS_DAO()
        url = "/notification/v1/person"
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        post_response = dao.postURL(url, headers, Serializer().serialize(person))

        #HTTP Status Code 201 Created: The request has been fulfilled and resulted
        #in a new resource being created
        if post_response.status != 201:
            raise DataFailureException(url, post_response.status, post_response.data)

        return post_response.status

    def update_person(self, person):
        """
        Update an existing person

        :param person:
        is the updated person that the client wants to update
        """
        #Validate
        self._validate_regid(person.person_id)
        self._validate_subscriber_id(person.surrogate_id)

        attributes = person.get_attributes()
        person.attributes = None

        for attribute in attributes:
            if attribute.name in MANAGED_ATTRIBUTES:
                continue

            person.add_attribute(attribute.name, attribute.value, None, None)
        #    ATTRIBUTE_TYPE_EMAIL_DISPATCHED_COUNT = 'DispatchedEmailCount'
        #    ATTRIBUTE_TYPE_SMS_DISPATCHED_COUNT = 'DispatchedTextMessageCount'
        #        ATTRIBUTE_TYPE_SMS_SENT_COUNT = 'SentTextMessageCount'
        #            ATTRIBUTE_TYPE_SUBSCRIPTION_COUNT = 'SubscriptionCount'

        dao = NWS_DAO()
        url = "/notification/v1/person/%s" % (person.person_id)
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        put_response = dao.putURL(url, headers, Serializer().serialize(person))

        #Http response code 204 No Content:
        #The server has fulfilled the request but does not need to return an entity-body
        if put_response.status != 204:
            raise DataFailureException(url, put_response.status, put_response.data)

        return put_response.status


    #SUBSCRIPTION RESOURCE
    def delete_subscription(self, subscription_id):
        """
        Deleting an existing subscription

        :param subscription_id:
        is the subscription that the client wants to delete
        """
        #Validate the subscription_id
        self._validate_uuid(subscription_id)

        #Delete the subscription
        url = "/notification/v1/subscription/%s" % (subscription_id)
        headers = {}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        dao = NWS_DAO()
        delete_response = dao.deleteURL(url, headers)

        #Http response code 204 No Content:
        #The server has fulfilled the request but does not need to return an entity-body
        if delete_response.status != 204:
            raise DataFailureException(url, delete_response.status, delete_response.data)

        return delete_response.status

    def update_subscription(self, subscription):
        """
        Update an existing subscription on a given channel

        :param subscription:
        is the updated subscription that the client wants to update
        """
        #Validate
        if subscription.get_channel() is not None:
            self._validate_uuid(subscription.get_channel().get_channel_id())
        if subscription.get_endpoint() is not None:
            if subscription.get_endpoint().get_endpoint_id() is not None:
                self._validate_uuid(subscription.get_endpoint().get_endpoint_id())
            self._validate_subscriber_id(subscription.get_endpoint().get_user_net_id())

        #Update the subscription
        dao = NWS_DAO()
        url = "/notification/v1/subscription/%s" % (subscription.subscription_id)
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        put_response = dao.putURL(url, headers, Serializer().serialize(subscription))

        #Http response code 204 No Content:
        #The server has fulfilled the request but does not need to return an entity-body
        if put_response.status != 204:
            raise DataFailureException(url, put_response.status, put_response.data)

        return put_response.status

    def create_new_subscription(self, subscription):
        """
        Create a new subscription

        :param subscription:
        is the new subscription that the client wants to create
        """
        #Validate input
        if subscription.get_subscription_id() is not None:
            self._validate_uuid(subscription.get_subscription_id())

        if subscription.get_endpoint() is not None:
            if subscription.get_endpoint().user:
                self._validate_subscriber_id(subscription.endpoint.user)

            if subscription.get_endpoint().get_endpoint_id() is not None:
                self._validate_uuid(subscription.endpoint.get_endpoint_id())

        if subscription.get_channel() is not None:
            self._validate_uuid(subscription.channel.get_channel_id())

        #Create new subscription
        dao = NWS_DAO()
        url = "/notification/v1/subscription"
        headers = {"Content-Type": "application/json"}
        if self.override_user is not None:
            headers['X_UW_ACT_AS'] = self.override_user

        post_response = dao.postURL(url, headers, Serializer().serialize(subscription))

        #HTTP Status Code 201 Created: The request has been fulfilled and resulted
        #in a new resource being created
        if post_response.status != 201:
            raise DataFailureException(url, post_response.status, post_response.data)

        return post_response.status

    def get_subscriptions_by_channel_id(self, channel_id):
        """
        Search for all subscriptions on a given channel
        """
        return self._get_subscriptions_from_nws(channel_id=channel_id)

    def get_subscriptions_by_subscriber_id(self, subscriber_id, max_results):
        """
        Search for all subscriptions by a given subscriber
        """
        return self._get_subscriptions_from_nws(subscriber_id=subscriber_id, max_results=max_results)

    def get_subscriptions_by_channel_id_and_subscriber_id(self, channel_id, subscriber_id):
        """
        Search for all subscriptions by a given channel and subscriber
        """
        return self._get_subscriptions_from_nws(channel_id=channel_id, subscriber_id=subscriber_id)

    def get_subscriptions_by_channel_id_and_person_id(self, channel_id, person_id):
        """
        Search for all subscriptions by a given channel and person
        """
        return self._get_subscriptions_from_nws(channel_id=channel_id, person_id=person_id)

    def get_subscription_by_channel_id_and_endpoint_id(self, channel_id, endpoint_id):
        """
        Search for subscription by a given channel and endpoint
        """
        subscriptions = []
        try:
            subscriptions = self._get_subscriptions_from_nws(channel_id=channel_id, endpoint_id=endpoint_id)
        except Exception as ex:
            raise

        return subscriptions[0]

    def _get_subscriptions_from_nws(self, *args, **kwargs):
        """
        Search for all subscriptions by a parameter
        """
        url = "/notification/v1/subscription" #?subscriber_id=%s" % (subscriber_id)

        number_of_args = len(kwargs)
        if number_of_args > 0:
            url += '?'
            for k,v in kwargs.iteritems():
                if k is not None and v is not None:
                    url += k + '=' + v
                    if number_of_args > 1:
                        url += '&'
                    number_of_args -= 1

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        subscriptions = SubscriptionList()
        Serializer().deserialize(subscriptions, response.data)

        return subscriptions.view_models

    #DISPATCH RESOURCE
    def create_new_message(self, dispatch):
        """
        Create a new dispatch

        :param dispatch:
        is the new dispatch that the client wants to create
        """

        #Create new dispatch
        dao = NWS_DAO()
        url = "/notification/v1/dispatch"

        data = Serializer().serialize(dispatch)

        post_response = dao.postURL(url, {"Content-Type": "application/json"}, data)

        if post_response.status != 200:
            raise DataFailureException(url, post_response.status, post_response.data)

        return post_response.status

    def retry_dispatch_queue(self):
        url = "/notification/v1/dispatch"
        dao = NWS_DAO()
        delete_response = dao.deleteURL(url, None)

        if delete_response.status != 202:
            raise DataFailureException(url, delete_response.status, delete_response.data)

        return delete_response

    def execute_job(self, job):
        url = "/notification/v1/job"

        data = Serializer().serialize(job)

        dao = NWS_DAO()
        post_response = dao.postURL(url, {"Content-Type": "application/json"}, data)

        if post_response.status != 201:
            raise DataFailureException(url, post_response.status, post_response.data)

        return post_response.status

    #CHANNEL RESOURCE
    def create_new_channel(self, channel):
        """
        Create a new channel

        :param channel:
        is the new channel that the client wants to create
        """
        #Create new channel
        dao = NWS_DAO()
        url = "/notification/v1/channel"

        post_response = dao.postURL(url, {"Content-Type": "application/json"}, Serializer().serialize(channel))

        #HTTP Status Code 201 Created: The request has been fulfilled and resulted
        #in a new resource being created
        if post_response.status != 201:
            raise DataFailureException(url, post_response.status, post_response.data)

        return post_response.status

    def update_channel(self, channel):
        """
        Update an existing channel

        :param channel:
        is the updated channel that the client wants to update
        """
        #Update the channel
        dao = NWS_DAO()
        url = "/notification/v1/channel/%s" % (channel.channel_id)

        put_response = dao.putURL(url, {"Content-Type": "application/json"}, Serializer().serialize(channel))

        #Http response code 204 No Content:
        #The server has fulfilled the request but does not need to return an entity-body
        if put_response.status != 204:
            raise DataFailureException(url, put_response.status, put_response.data)

        return put_response.status

    def delete_channel(self, channel_id):
        """
        Deleting an existing channel

        :param channel_id:
        is the channel that the client wants to delete
        """

        #Validate the subscription_id
        self._validate_uuid(channel_id)

        #Delete the subscription
        url = "/notification/v1/channel/%s" % (channel_id)
        dao = NWS_DAO()
        delete_response = dao.deleteURL(url, None)

        #Http response code 204 No Content:
        #The server has fulfilled the request but does not need to return an entity-body
        if delete_response.status != 204:
            raise DataFailureException(url, delete_response.status, delete_response.data)

        return delete_response.status

    def get_channel_by_channel_id(self, channel_id):
        """
        Get a channel by channel id
        """
        #Validate the channel_id
        self._validate_uuid(channel_id)

        url = "/notification/v1/channel/%s" % (channel_id)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        channel = Channel()
        Serializer().deserialize(channel, response.data)

        return channel

    def get_channel_by_surrogate_id(self, channel_type, surrogate_id):
        """
        Get a channel by surrogate id
        """
        key = "%s|%s" % (channel_type, surrogate_id)
        url = "/notification/v1/channel/%s" % (quote(key))

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        channel = Channel()
        Serializer().deserialize(channel, response.data)

        return channel

    def get_channels_by_sln(self, channel_type, sln):
        """
        Search for all channels by sln
        """
        url = "/notification/v1/channel?type=%s&tag_sln=%s" % (channel_type, sln)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        channel_list = ChannelList()
        Serializer().deserialize(channel_list, response.data)

        return channel_list.view_models

    def get_channels_by_sln_year_quarter(self, channel_type, sln, year, quarter):
        """
        Search for all channels by sln, year and quarter
        """
        url = "/notification/v1/channel?type=%s&tag_sln=%s&tag_year=%s&tag_quarter=%s" % (channel_type, sln, year, quarter)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        channel_list = ChannelList()
        Serializer().deserialize(channel_list, response.data)

        return channel_list.view_models

    def term_has_active_channel(self, channel_type, term):
        """
        Checks to see if there exists a channel for the given sws.Term object's
        year and quarter.
        """
        #Sets now to midnight of current day to allow for caching
        now = datetime.combine(datetime.utcnow().date(), time.min).isoformat()

        dao = NWS_DAO()
        url = "/notification/v1/channel?tag_year=%s&tag_quarter=%s&max_results=1&expires_after=%s" % (term.year, term.quarter, now)
        response = dao.getURL(url, {"Accept": "application/json"})
        if response.status != 200:
            return False

        data = json.loads(response.data)
        if "TotalCount" in data:
            if data["TotalCount"] > 0:
                return True

        return False

    def get_terms_with_active_channels(self, channel_type):
        """
        Returns a list of all sws.Terms that have active channels.
        """
        # Check the current term, and the next 3, to see if they have
        # a channel for any course in that term.
        # when the sws term resource provides us with a timeschedule publish
        # date, use that instead of this.
        term = get_current_term()
        terms = []
        if self.term_has_active_channel(channel_type, term):
            terms.append(term)

        for i in range(3):
            term = get_term_after(term)
            if self.term_has_active_channel(channel_type, term):
                terms.append(term)

        return terms

    def get_channels(self, first_result = 1, max_results = 10):
        """
        Search for all channels
        """
        url = "/notification/v1/channel?first_result=%s&max_results=%s" % (first_result, max_results)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        channel_list = ChannelList()
        Serializer().deserialize(channel_list, response.data)

        return channel_list.view_models

    def get_course_available_event(self, body):
        """
        This is responsible for parsing the message body out of an SQS message
        """
        event = CourseAvailableEvent()

        body = json.loads(body)
        message = json.loads(body["Message"])
        message_timestamp = body["Timestamp"]
        message_body = json.loads(message["Body"])
        event_data = message_body["Event"]

        event.event_id = event_data["EventID"]
        event.event_create_date = event_data["EventCreateDate"]
        event.message_timestamp = message_timestamp
        event.year = event_data["Section"]["Course"]["Year"]
        event.quarter = event_data["Section"]["Course"]["Quarter"]
        event.curriculum_abbr = event_data["Section"]["Course"]["CurriculumAbbreviation"]
        event.course_number = event_data["Section"]["Course"]["CourseNumber"]
        event.section_id = event_data["Section"]["SectionID"]
        event.space_available = event_data["SpaceAvailable"]
        event.sln = event_data["Section"]["SLN"]
        if event.space_available <= 0:
            event.notification_msg_0 = " NO"

        return event

    def get_person_by_surrogate_id(self, surrogate_id):
        #Validate input
        self._validate_subscriber_id(surrogate_id)

        url = "/notification/v1/person/%s" % (surrogate_id)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        person = Person()
        Serializer().deserialize(person, response.data)
        return person

    def get_person_by_uwregid(self, uwregid):
        url = "/notification/v1/person/%s" % (uwregid)

        dao = NWS_DAO()
        response = dao.getURL(url, {"Accept": "application/json"})

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        person = Person()
        Serializer().deserialize(person, response.data)
        return person

    def _validate_uuid(self, id):
        if id is None:
            raise InvalidUUID(id)
        if not re.match(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', id):
            raise InvalidUUID(id)

    def _validate_regid(self, id):
        if id is None:
            raise InvalidRegID(id)
        if not re.match(r'^[0-9A-F]{32}$', id):
            raise InvalidRegID(id)

    def _validate_subscriber_id(self, subscriber_id):
        if subscriber_id is None or subscriber_id == '':
            raise InvalidNetID(subscriber_id)
        if not re.match(r'^([a-z]adm_)?[a-z][a-z0-9]{0,7}(@washington.edu)?$', subscriber_id, re.I):
            raise InvalidNetID(subscriber_id)

    def _validate_endpoint_protocol(self, protocol):
        if not re.match(r'^(Email|SMS)$', protocol, re.I):
            raise InvalidEndpointProtocol(protocol)
