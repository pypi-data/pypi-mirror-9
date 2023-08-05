"""
Deuce Client - Project API
"""
from stoplight import validate

from deuceclient.api.vault import Vault
from deuceclient.common.validation import *


class Project(dict):
    """
    Collection for a given project_id that contains the vaults associated
    with that project_id
    """

    @validate(project_id=ProjectIdRule)
    def __init__(self, project_id):
        super(Project, self).__init__()
        self.__properties = {
            'marker': None,
            'project_id': project_id,
        }

    @property
    def project_id(self):
        return self.__properties['project_id']

    @validate(key=VaultIdRule)
    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    @validate(key=VaultIdRule)
    def __setitem__(self, key, val):
        if isinstance(val, Vault):
            return dict.__setitem__(self, key, val)
        else:
            raise TypeError(
                '{0} can only contain Vaults'.format(self.__class__))

    @property
    def marker(self):
        return self.__properties['marker']

    @marker.setter
    @validate(value=VaultIdRuleNoneOkay)
    def marker(self, value):
        # Note: We could force that "marker" is in the dict;
        #   but then that would also unnecessarily force
        #   order-of-operations on how to use the object
        self.__properties['marker'] = value

    def __repr__(self):
        return '{0}: "{1}" - {2}'.format(type(self).__name__,
                                         self.project_id,
                                         dict.__repr__(self))

    def update(self, *args, **kwargs):
        # Force use of Project.__setitem__ in order
        # to get validation of each entry in the incoming dictionary
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
