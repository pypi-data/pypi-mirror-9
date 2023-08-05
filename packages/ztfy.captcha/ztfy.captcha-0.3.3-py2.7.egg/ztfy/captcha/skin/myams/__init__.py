#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages
from fanstatic import Library, Resource

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.myams import jquery


library = Library('ztfy.captcha.myams', 'resources')

captcha = Resource(library, 'js/ztfy.captcha.js',
                   depends=(jquery, ),
                   bottom=True)
