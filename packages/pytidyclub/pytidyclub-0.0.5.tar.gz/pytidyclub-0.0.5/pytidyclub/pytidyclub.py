#!/usr/bin/env python

# pytidyclub
#
# A Python wrapper for the TidyClub API.

import requests
import urllib


__VERSION__ = "0.0.5"


class Club:
    slug = None
    token = None
    client_id = None
    client_secret = None
    ERRORS = {
        400: "Bad Request: Unable to pass parameters",
        401: "Unauthorized: Access token was missing or incorrect",
        403: "Forbidden: Accessing restricted area without appropriate " +
             "user privileges",
        404: "Not Found: The URI requested is invalid or the resource " +
             "requested, such as a contact, does not exists.",
        406: "Not Acceptable: Returned when an invalid format is specified " +
             "in the request.",
        422: "Unprocessable Entity: Sending invalid fields will result in " +
             "an unprocessable entity response.",
    }

    def __init__(self, slug, client_id, client_secret):
        """
        Initialise a Club instance.

        Keyword arguments:
        slug -- the subdomain 'slug' that this club has been assigned by
                TidyClub.
        client_id -- The OAuth client ID as prescribed by TidyClub.
        client_secret -- the OAuth client secret as prescribed by TidyClub.
        """
        self.slug = slug
        self.client_id = client_id
        self.client_secret = client_secret

    ######
    # Authorization.
    ######

    def auth_authcode_get_url(self, redirect_uri):
        """
        Generate and return a URL to initiate the 'Authorization Code' OAuth
        authorization flow.

        One of the many authorization flows offered by the TidyClub API is
        the Authorization code flow. The Authorization Code flow is the most
        popular authorization flow, and begins with the end user opening a
        special authorization URL.

        See the TidyClub API for more information.
        https://dev.tidyclub.com/api/authentication

        redirect_uri -- The redirection URI that you specified when generating
                        your TidyClub API token.
        """
        return self._url("oauth/authorize?") + urllib.urlencode({
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
        })

    def auth_authcode_exchange_code(self, code, redirect_uri):
        """
        Take a temporary authorization code and use it to authorize the Club
        object.

        Use this as the second half of the Authorization Code flow.

        Keyword arguments:
        code -- the temporary authorization code provided to you, usually by
                auth_authcode_get_url().
        redirect_uri -- the redirection URI you chose when signing up for the
                        TidyClub API.
        """
        response = self._call("oauth/token", {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
            "grant_type": "authorization_code"
        }, method="POST", prefix="", auth_required=False)

        self.token = response['payload']['access_token']

    def auth_user_credentials(self, username, password):
        """
        Authorize with the 'resource owner password credentials' workflow.

        This workflow authorizes based on a user's username and password.

        It is not recommended that you use this workflow due to the potential
        leak of user credentials.

        Keyword arguments:
        username -- the username portion of the credentials you wish to use to
                    authenticate.
        password -- the password portion of the credentials you wish to use to
                    authenticate, in plain text.
        """
        response = self._call("oauth/token", {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
            "grant_type": "password"
        }, method="POST", prefix="", auth_required=False)

        self.token = response['payload']['access_token']

    ######
    # Club
    ######

    def info(self):
        return self._call('club', auth_required=False)

    ######
    # Contacts
    ######

    def contacts(self, search_terms=None, group=None, registered=None,
                 limit=0, offset=0):
        """
        Get a list of all contacts associated with the club.

        Keyword arguments:
        search_terms -- server-side fuzzy searching that will be applied to
                        the list prior to a limit/offset being enforced.
        group -- the ID of a group to constrain the search to, as opposed to
                 all contacts in the club.
        registered -- undocumented in the API, unsure.
        limit -- limit the returned result to this many entires.
        offset -- offset the returned result by this many entries.
        """

        # The API has a different endpoint for group searches.
        if group:
            path = "groups/{group}/contacts".format(group=group)
        else:
            path = "contacts"

        data = {
            "limit": limit,
            "offset": offset
        }

        data['group'] = group if group else None
        data['search_terms'] = search_terms if search_terms else None
        data['registered'] = registered if registered else None

        response = self._call(path, data, "GET")

        return response['payload']

    ######
    # Groups
    ######

    def groups(self):
        response = self._call('groups')
        return response['payload']

    ######
    # Tasks
    ######
    def tasks(self, contact_id=None, completed=None, limit=0, offset=0):
        """
        Get a list of all tasks associated with the club.

        Keyword arguments:
        contact_id -- if supplied, only return tasks associated with this
                      contact.
        completed -- if True, only return tasks that have been completed. If
                     False only return tasks that are imcomplete. If None,
                     return all tasks that meet any other defined conditions in
                     the function call.
        limit -- limit the returned result to this many entires.
        offset -- offset the returned result by this many entries.
        """
        if contact_id:
            path = 'contacts/{id}/tasks'.format(id=contact_id)
        else:
            path = 'tasks'

        data = {
            "limit": limit,
            "offset": offset
        }

        if completed is True:
            data['completed'] = 'true'
        elif completed is False:
            data['completed'] = 'false'

        response = self._call(path, data, "GET")

        return response['payload']

    def add_task(self, title, description, due, contact_id, category_id):
        """
        Add a task.

        Keyword arguments:
        title -- the task's title.
        description -- the task's description.
        due -- the due date (YYYY-MM-DD).
        contact_id -- the unique ID of the contact to assign the task to.
        category_id -- the unique ID of the category that best fits this task.
        """
        data = {
            'title': title,
            'description': description,
            'due_date': due,
            'contact_id': contact_id,
            'category_id': category_id
        }

        response = self._call('tasks/add', data, "POST")
        return response['payload']

    ######
    # Categories
    ######
    def categories(self, limit=0, offset=0):
        """
        Get a list of all categories associated with the club.

        Keyword arguments:
        limit -- limit the returned result to this many entires.
        offset -- offset the returned result by this many entries.
        """

        data = {
            "limit": limit,
            "offset": offset
        }

        response = self._call('categories', data, "GET")
        return response['payload']

    ######
    # Helper methods
    #####

    def _call(self, path, data=None, method="GET", prefix="api/v1/",
              headers=None, decode_json=True, auth_required=True):
        # If auth is required, include the auth header.
        if auth_required:
            if self.authorized:
                if headers is None:
                    headers = {}
                headers["Authorization"] = "Bearer %s" % self.token
            else:
                raise PyTCAuthorizationError("Attempted to make an authorized "
                                             "call while not authorized")

        # Construct the call URL and make the request.
        url = self._url(prefix + path)
        response = requests.request(method, url, data=data, headers=headers)

        # Check for API errors
        if response.status_code in self.ERRORS.keys():
            # One of TidyClub's documented error codes has been caught (as
            # opposed to a positive response). Attempt to get more information
            # by checking if any JSON error data has been provided. If not,
            # fall back to a hard-coded set of error codes/descriptions, as
            # provided in the TidyClub API docs.
            try:
                error_json = response.json()
                tc_error = error_json['error']
                tc_error_desc = error_json['error_description']
            except ValueError:
                tc_error = response.status_code
                tc_error_desc = self.ERRORS[response.status_code]

            raise PyTCUpstreamError(tc_error, tc_error_desc)
        else:
            # Based on HTTP status code, a correct response was received.
            # Return a dictionary of the HTTP status code and the payload
            # received.
            payload = response.json() if decode_json else response.content
            return {
                "payload": payload,
                "code": response.status_code
            }

    def _url(self, path):
        return "https://%s.tidyclub.com/%s" % (self.slug, path)

    @property
    def authorized(self):
        return not (self.token is None)


#####
# Exceptions
#####


class PyTCError(Exception):
    """The base pytidyclub exception class.

    All pytidyclub-raised exceptions will be of (or inherit from) this class.
    """
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return repr(self.error)


class PyTCUpstreamError(PyTCError):
    """TidyClub API error.

    Raised when an error has been returned by the TidyClub API as the result
    of an API call.

    error -- the error name, as per the TidyClub API response.
    error_description -- the error description, as per the TidyClub API
                         documentation.
    """
    def __init__(self, error, error_description):
        self.error = error
        self.error_description = error_description

    def __str__(self):
        return ("A TidyClub API error has been encountered: {ex.error}' "
                "- {ex.error_description}".format(ex=self))


class PyTCAuthorizationError(PyTCError):
    pass
