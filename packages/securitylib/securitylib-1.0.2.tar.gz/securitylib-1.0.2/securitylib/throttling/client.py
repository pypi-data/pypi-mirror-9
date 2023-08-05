__all__ = ['StateChecker']

# FEATURES
# Allow overriding limits - CHECK
# Allow captcha or block not to be used - CHECK
# Allow overriding expiration times - CHECK
# Allow changing format of storage keys - CHECK
# Easy to use asynchronously (client should not need to wait for the throttling module before returning an answer to the user) - CHECK
# Independent of the storage method (accept any object following memcache interface) - CHECK
# Allow captcha from services - CHECK
# First time showing a login page to a user, no login attempt has been made, but it should be possible to show the throttling state to the user (a captcha form or a block timeout) - CHECK
# Allow throttling of other requests besides login (registration, password recovery, POSTs in general) - CHECK
# Different storage keys for counters of different functionalities (registration, password recovery) - CHECK

# Provide helper functions for most common implementations (using memcache, synchronous, etc.)


class StateChecker(object):
    """
    Use this class to check the throttling state of client requests.

    :param counters_storage: Storage to be used for storing throttling counters.
    :type counters_storage: :class:`securitylib.throttling.common.CountersStorage`

    :param session_storage: Storage to be used to store sessions.
    :type session_storage: :class:`securitylib.throttling.common.SessionStorage`
    """

    def __init__(self, counters_storage, session_storage):
        self.counters_storage = counters_storage
        self.session_storage = session_storage

    def check_state(self, ip, user=None, pwd=None, session_id=None, ctx=''):
        """
        Returns the throttling state for a given request.
        You should call this method before processing a request to find out if a request should be blocked,
        if a captcha must be validated before processing the request, or if no action is needed before proceeding.
        You can also call this method before presenting a page to the user in order to find out
        what you should present: a message saying the user is blocked, a captcha for the user to
        fill, or neither.

        :param ip: The ip of the client that made the request.
        :type ip: :class:`str`

        :param user: The user that the client sent in his login request. (used for login attempts)
        :type user: :class:`str`

        :param pwd: The password that the client sent in his login request. (used for login attempts)
        :type pwd: :class:`str`

        :param session_id: The session_id for the client's session. This session_id should be generated using
            :func:`~securitylib.random.get_random_token` or another function with the same properties,
            and should be stored in a cookie in the client's browser.
            This session_id is to be used for thottling purposes only and so should persist even after the
            user logs out of the application, contrary to typical sessions.
            This session_id is used only for login requests and thus can be omitted for other requests.
        :type session_id: :class:`str`

        :param ctx: The context of the request. Use this if you want to have different throttling counters for different
            parts of your application. For example, you might want to separate the throttling for login requests from
            that of password recovery requests, meaning that a user can be blocked from sending login requests but
            can still try a password recovery.
            Each string will access different counters, so make sure that you always use the same string for a given context.
        :type ip: :class:`str`

        :returns: :class:`dict` -- A dictionary with the requested throttling state. It always has a 'state' key
            which can have three values: 'ok', 'captcha' and 'block' (meaning should be obvious from the documentation above).
            If 'state' is 'block' there is an additional key called 'unblock_timestamp' which will contain a timestamp
            of the time when the 'block' state will end. This can be used to tell the client when he will be
            unblocked.
        """
        if session_id:
            session = self.session_storage.get(session_id)
            if session and user and session.has_valid_login(user):
                return {'state': 'ok'}

        counters = self.counters_storage.get(ip, user, pwd, ctx)
        response = counters.get_info()
        return response
