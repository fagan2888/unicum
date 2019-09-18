# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


__doc__ = 'Python library for simple object cache and factory.'
__version__ = '0.3'
__dev_status__ = '4 - Beta'
__date__ = 'Wednesday, 18 September 2019'
__author__ = 'sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]'
__email__ = 'sonntagsgesicht@icloud.com'
__url__ = 'https://github.com/sonntagsgesicht/' + __name__
__license__ = 'Apache License 2.0'
__dependencies__ = ()
__dependency_links__ = ()
__data__ = ()
__scripts__ = ()


from .singletonobject import *
from .factoryobject import *
from .linkedobject import *
from .persistentobject import *
from .datarange import *
from .visibleobject import *
from .session import *
