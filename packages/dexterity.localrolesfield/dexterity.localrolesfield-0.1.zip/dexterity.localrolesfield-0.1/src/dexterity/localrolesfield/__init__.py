# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory

import logging

_ = MessageFactory('dexterity.localrolesfield')

logger = logging.getLogger('dexterity.localrolesfield')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
