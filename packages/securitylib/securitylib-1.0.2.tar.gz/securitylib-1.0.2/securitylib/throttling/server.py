from time import mktime
import datetime
from .common import Session

__all__ = ['StateUpdater']


class StateUpdater(object):
    """
    Use this class to update the throttling state of client requests.

    :param counters_storage: Storage to be used for storing throttling counters.
    :type counters_storage: :class:`securitylib.throttling.common.CountersStorage`

    :param session_storage: Storage to be used to store sessions.
    :type session_storage: :class:`securitylib.throttling.common.SessionStorage`

    :param config: A dictionary containing throttling parameters (dictionary keys are the parameter name
        and dictionary values are the parameter value).
        Allows defining the limits in requests before the throttling state changes to captcha or block,
        and the initial blocking time.

        You can omit the whole dictionary or some of its keys as the values
        for the missing keys will be taken from the default configuration.

            *Structure*:

            +---------------------------+---------------------------------------------------+-----------------------------------------------------------------------------------+
            | Key                       | Type                                              | Description                                                                       |
            +===========================+===================================================+===================================================================================+
            | ``limits``                | *dictionary of dictionaries with integer values*  | This parameter must have up to two dictionaries with keys ``'captcha'``           |
            |                           |                                                   | and ``'block'``, one that contains captcha limits, and another for block limits.  |
            |                           |                                                   |                                                                                   |
            |                           |                                                   | If any of these dictionaries is missing, no limits will be imposed                |
            |                           |                                                   | for that throttling method, which effectively disables the throttling method.     |
            |                           |                                                   | This can be used, for example, to disable throttling by captcha for APIs.         |
            |                           |                                                   |                                                                                   |
            |                           |                                                   | Each of these two dictionaries has up to five pairs of keys and values,           |
            |                           |                                                   | where each key is a type of counter and its value                                 |
            |                           |                                                   | is the limit for the value of the counter before the throttling state is updated, |
            |                           |                                                   | e.g. if ``limits['captcha']['user']`` is 5, the state for the ``'user'`` counter  |
            |                           |                                                   | will change to ``'captcha'`` when its value increases beyond 5.                   |
            +---------------------------+---------------------------------------------------+-----------------------------------------------------------------------------------+
            | ``initial_blocking_time`` | *integer*                                         | Duration in seconds for the first block (subsequent blocks will have              |
            |                           |                                                   | its duration doubled each time).                                                  |
            +---------------------------+---------------------------------------------------+-----------------------------------------------------------------------------------+

            *Default configuration*::

                {
                    'limits': {
                        'captcha': {
                            'ip': 20,
                            'user': 20,
                            'pwd': 20,
                            'ip_user': 3,
                            'ip_pwd': 3,
                        },
                        'block': {
                            'ip': 100,
                            'user': None,
                            'pwd': None,
                            'ip_user': 7,
                            'ip_pwd': 7,
                        },
                    },
                    'initial_blocking_time': 30,
                }
    :type config: :class:`dict`
    """

    DEFAULT_CONFIG = {
        'limits': {
            'captcha': {
                'ip': 20,
                'user': 20,
                'pwd': 20,
                'ip_user': 3,
                'ip_pwd': 3,
            },
            'block': {
                'ip': 100,
                'user': None,
                'pwd': None,
                'ip_user': 7,
                'ip_pwd': 7,
            },
        },
        'initial_blocking_time': 30,
    }

    FREE_PASS_LIMIT = 10

    def __init__(self, counters_storage, session_storage, config=None):
        self.counters_storage = counters_storage
        self.session_storage = session_storage
        if not config:
            config = {}
        self.limits = config.get('limits', self.DEFAULT_CONFIG['limits'])
        self.initial_blocking_time = config.get('initial_blocking_time', self.DEFAULT_CONFIG['initial_blocking_time'])

    def add_request(self, ip, user=None, pwd=None, session_id=None, success=False, ctx=''):
        """
        Notifies the StateUpdater of the ocurrence of a request, which it will use to update the respective counters
        and their state.

        :param ip: The ip of the client that made the request.
        :type ip: :class:`str`

        :param user: The user that the client sent in his login request. (used for login attempts)
        :type user: :class:`str`

        :param pwd: The password that the client sent in his login request. (used for login attempts)
        :type pwd: :class:`str`

        :param session_id: The session_id for the client's session.
            Use the same session_id you used in the :func:`check_state` call.
            This session_id is used only for login requests and thus can be omitted for other requests.
        :type session_id: :class:`str`

        :param success: Whether the given request succeeded or not. This applies to a login request, for example,
            where the login can either succeed or not. Most other requests have no such differentiation, and as such you should
            omit this parameter.
        :type success: :class:`bool`

        :param ctx: The context of the request.
            Use the same context you used in the :func:`check_state` call.
        :type ip: :class:`str`
        """
        counters = self.counters_storage.get(ip, user, pwd, ctx)
        self._update_counters_values(counters, success)
        self._update_counters_status(counters)
        self.counters_storage.set(ip, user, pwd, counters, ctx)
        if session_id and user:
            session = self.session_storage.get(session_id)
            if not session:
                session = Session()

            if success:
                session.add_valid_login(user)
            elif session.has_valid_login(user):
                failed_attempts = session.add_failed_attempt(user)
                if failed_attempts >= self.FREE_PASS_LIMIT:
                    session.remove_valid_login(user)

            self.session_storage.set(session_id, session)

    def _update_counters_values(self, counters, success=False):
        if success:
            if 'user' in counters:
                counters['ip_user'].value = 0
        else:
            counters['ip'].value += 1
            if 'user' in counters:
                counters['ip_user'].value += 1
                if counters['ip_user'].value == 1:
                    counters['user'].value += 1
            if 'pwd' in counters:
                counters['ip_pwd'].value += 1
                if counters['ip_pwd'].value == 1:
                    counters['pwd'].value += 1

    def _update_counters_status(self, counters):
        for counter_name, counter in counters.iteritems():
            try:
                block_limit = self.limits['block'][counter_name]
            except KeyError:
                block_limit = None
            try:
                captcha_limit = self.limits['captcha'][counter_name]
            except KeyError:
                captcha_limit = None

            if block_limit is not None and counter.value >= block_limit:
                counter.state = 'block'
                counter.attributes.setdefault('n_blocks', 0)
                block_expire_time = self._get_block_expire_time(counter.attributes['n_blocks'])
                unblock_datetime = datetime.datetime.now() + datetime.timedelta(seconds=block_expire_time)
                counter.attributes['unblock_timestamp'] = int(mktime(unblock_datetime.timetuple()))
                counter.attributes['n_blocks'] += 1
            elif captcha_limit is not None and counter.value >= captcha_limit:
                counter.state = 'captcha'
            else:
                counter.state = 'ok'

    def _get_block_expire_time(self, n_previous_blocks):
        return self.initial_blocking_time * 2 ** n_previous_blocks
