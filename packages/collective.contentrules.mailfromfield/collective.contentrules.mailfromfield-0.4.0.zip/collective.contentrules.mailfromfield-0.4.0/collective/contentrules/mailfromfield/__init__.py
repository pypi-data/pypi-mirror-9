# -*- coding: utf-8 -*-
from logging import getLogger
from zope.i18nmessageid import MessageFactory


logger = getLogger('collective.contentrules.mailfromfield')
messageFactory = MessageFactory('collective.contentrules.mailfromfield')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
