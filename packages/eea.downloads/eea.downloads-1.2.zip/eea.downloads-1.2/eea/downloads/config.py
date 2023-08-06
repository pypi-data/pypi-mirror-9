"""Common configuration constants
"""
import os

PROJECTNAME = 'eea.downloads'

def ENVPATH():
    """ GET EEADOWNLOADS_PATH from os env
    """
    return os.environ.get('EEADOWNLOADS_PATH')

def ENVNAME():
    """ Get EEADOWNLOADS_NAME from os env
    """
    return os.environ.get('EEADOWNLOADS_NAME')

from zope.i18nmessageid import MessageFactory
EEAMessageFactory = MessageFactory('eea')
