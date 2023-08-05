###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

import json

from autobahn import util
from autobahn.wamp.exception import ProtocolError

__all__ = ('RoleFeatures',
           'RoleBrokerFeatures',
           'RoleSubscriberFeatures',
           'RolePublisherFeatures',
           'RoleDealerFeatures',
           'RoleCallerFeatures',
           'RoleCalleeFeatures',
           'ROLE_NAME_TO_CLASS')


class RoleFeatures(util.EqualityMixin):

    ROLE = None

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        configured_options = {}
        for k, v in self.__dict__.items():
            if v is not None:
                configured_options[k] = v
        return "{0}({1})".format(self.ROLE, ", ".join([k + '=' + str(v)
                                                       for k, v in configured_options.items()]))

    def _check_all_bool(self):
        # check feature attributes
        for k in self.__dict__:
            if not k.startswith('_') and k != 'ROLE':
                if getattr(self, k) is not None and type(getattr(self, k)) != bool:
                    raise ProtocolError("invalid type {0} for feature '{1}' for role '{2}'".format(getattr(self, k), k, self.ROLE))


class RoleCommonPubSubFeatures(RoleFeatures):

    def __init__(self,
                 publisher_identification=None,
                 partitioned_pubsub=None):

        self.publisher_identification = publisher_identification
        self.partitioned_pubsub = partitioned_pubsub


class RoleBrokerFeatures(RoleCommonPubSubFeatures):

    ROLE = u'broker'

    def __init__(self,
                 subscriber_blackwhite_listing=None,
                 publisher_exclusion=None,
                 publication_trustlevels=None,
                 pattern_based_subscription=None,
                 subscriber_metaevents=None,
                 subscriber_list=None,
                 event_history=None,
                 **kwargs):
        self.subscriber_blackwhite_listing = subscriber_blackwhite_listing
        self.publisher_exclusion = publisher_exclusion
        self.publication_trustlevels = publication_trustlevels
        self.pattern_based_subscription = pattern_based_subscription
        self.subscriber_metaevents = subscriber_metaevents
        self.subscriber_list = subscriber_list
        self.event_history = event_history
        RoleCommonPubSubFeatures.__init__(self, **kwargs)
        self._check_all_bool()


class RoleSubscriberFeatures(RoleCommonPubSubFeatures):

    ROLE = u'subscriber'

    def __init__(self,
                 publication_trustlevels=None,
                 pattern_based_subscription=None,
                 subscriber_metaevents=None,
                 subscriber_list=None,
                 event_history=None,
                 **kwargs):
        self.publication_trustlevels = publication_trustlevels
        self.pattern_based_subscription = pattern_based_subscription
        self.subscriber_metaevents = subscriber_metaevents
        self.subscriber_list = subscriber_list
        self.event_history = event_history
        RoleCommonPubSubFeatures.__init__(self, **kwargs)
        self._check_all_bool()


class RolePublisherFeatures(RoleCommonPubSubFeatures):

    ROLE = u'publisher'

    def __init__(self,
                 subscriber_blackwhite_listing=None,
                 publisher_exclusion=None,
                 **kwargs):
        self.subscriber_blackwhite_listing = subscriber_blackwhite_listing
        self.publisher_exclusion = publisher_exclusion
        RoleCommonPubSubFeatures.__init__(self, **kwargs)
        self._check_all_bool()


class RoleCommonRpcFeatures(RoleFeatures):

    def __init__(self,
                 caller_identification=None,
                 partitioned_rpc=None,
                 call_timeout=None,
                 call_canceling=None,
                 progressive_call_results=None):
        self.caller_identification = caller_identification
        self.partitioned_rpc = partitioned_rpc
        self.call_timeout = call_timeout
        self.call_canceling = call_canceling
        self.progressive_call_results = progressive_call_results


class RoleDealerFeatures(RoleCommonRpcFeatures):

    ROLE = u'dealer'

    def __init__(self,
                 callee_blackwhite_listing=None,
                 caller_exclusion=None,
                 call_trustlevels=None,
                 pattern_based_registration=None,
                 **kwargs):
        self.callee_blackwhite_listing = callee_blackwhite_listing
        self.caller_exclusion = caller_exclusion
        self.call_trustlevels = call_trustlevels
        self.pattern_based_registration = pattern_based_registration
        RoleCommonRpcFeatures.__init__(self, **kwargs)
        self._check_all_bool()


class RoleCallerFeatures(RoleCommonRpcFeatures):

    ROLE = u'caller'

    def __init__(self,
                 callee_blackwhite_listing=None,
                 caller_exclusion=None,
                 **kwargs):
        self.callee_blackwhite_listing = callee_blackwhite_listing
        self.caller_exclusion = caller_exclusion
        RoleCommonRpcFeatures.__init__(self, **kwargs)
        self._check_all_bool()


class RoleCalleeFeatures(RoleCommonRpcFeatures):

    ROLE = u'callee'

    def __init__(self,
                 call_trustlevels=None,
                 pattern_based_registration=None,
                 **kwargs):
        self.call_trustlevels = call_trustlevels
        self.pattern_based_registration = pattern_based_registration
        RoleCommonRpcFeatures.__init__(self, **kwargs)
        self._check_all_bool()


ROLE_NAME_TO_CLASS = {
    u'broker': RoleBrokerFeatures,
    u'subscriber': RoleSubscriberFeatures,
    u'publisher': RolePublisherFeatures,
    u'dealer': RoleDealerFeatures,
    u'caller': RoleCallerFeatures,
    u'callee': RoleCalleeFeatures,
}
