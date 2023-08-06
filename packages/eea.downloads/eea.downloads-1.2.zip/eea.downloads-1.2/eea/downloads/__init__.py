""" Main product initializer
"""
from eea.downloads.config import ENVPATH, ENVNAME
from eea.downloads.content.DirectoryView import registerDirectory

def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    path = ENVPATH()
    if not path:
        raise AttributeError('Missing environment var EEADOWNLOADS_PATH')

    name = ENVNAME()
    if not name:
        raise AttributeError('Missing environment var EEADOWNLOADS_NAME')

    registerDirectory(path)
