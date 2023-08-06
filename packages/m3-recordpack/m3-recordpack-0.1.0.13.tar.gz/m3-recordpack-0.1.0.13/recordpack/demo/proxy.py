# coding: utf-8
u""" Module description. 
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# 3rdparty
from django.db import models

# Recordpack
from recordpack.provider import BaseProxy

#------------------------------------------------------------------------------
# Proxies
#------------------------------------------------------------------------------

class PersonListProxy(BaseProxy):
    def load(self, root):
        person_model = models.get_model('demo', 'Person')
        self.from_root()
        self.gender = person_model.GENDERS[self.gender]
