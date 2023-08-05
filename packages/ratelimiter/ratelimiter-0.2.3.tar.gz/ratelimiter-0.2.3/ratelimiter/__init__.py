# Original work Copyright 2013 Arnaud Porterie
# Modified work Copyright 2015 Frazer McLean
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import functools
import threading
import time

__author__ = 'Frazer McLean <frazer@frazermclean.co.uk>'
__version__ = '0.2.3'
__license__ = 'Apache'
__description__ = 'Simple python rate limiting object'


class RateLimiter(object):
    """Provides rate limiting for an operation with a configurable number of
    requests for a time period.
    """

    def __init__(self, max_calls, period=1.0, callback=None):
        """Initialze a RateLimiter objects which enforces as much as max_calls
        operations on period (eventually floating) number of seconds.
        """
        if period <= 0:
            raise ValueError('Rate limiting period should be > 0')
        if max_calls <= 0:
            raise ValueError('Rate limiting number of calls should be > 0')

        # We're using a deque to store the last execution timestamps, not for
        # its maxlen attribute, but to allow constant time front removal.
        self.calls = collections.deque()

        self.period = period
        self.max_calls = max_calls
        self.callback = callback

    def __call__(self, f):
        """The __call__ function allows the RateLimiter object to be used as a
        regular function decorator.
        """
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                return f(*args, **kwargs)
        return wrapped

    def __enter__(self):
        # We want to ensure that no more than max_calls were run in the allowed
        # period. For this, we store the last timestamps of each call and run
        # the rate verification upon each __enter__ call.
        if len(self.calls) >= self.max_calls:
            until = time.time() + self.period - self._timespan
            if self.callback:
                t = threading.Thread(target=self.callback, args=(until,))
                t.daemon = True
                t.start()
            time.sleep(until - time.time())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Store the last operation timestamp.
        self.calls.append(time.time())

        # Pop the timestamp list front (ie: the older calls) until the sum goes
        # back below the period. This is our 'sliding period' window.
        while self._timespan >= self.period:
            self.calls.popleft()

    @property
    def _timespan(self):
        return self.calls[-1] - self.calls[0]
