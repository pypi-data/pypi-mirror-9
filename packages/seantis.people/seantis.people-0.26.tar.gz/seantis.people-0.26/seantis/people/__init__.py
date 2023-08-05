import logging
log = logging.getLogger('seantis.people')

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('seantis.people')

# duplicated in profiles/default/toolset/toolset.xml
catalog_id = 'seantis_people_catalog'

import warnings
from exceptions import UnicodeWarning
warnings.filterwarnings('error', category=UnicodeWarning)
