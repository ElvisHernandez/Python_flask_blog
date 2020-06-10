from .config import CRUD
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(funcName)s:%(message)s')	
file_handler = logging.FileHandler(os.path.abspath('logs') + '/RoleModel.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

class Permissions:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(CRUD):
    tablename = "roles"
    def __init__(self,**columns):
        self.id = columns.get('id',None)
        self.name = columns.get('name',None)
        self.default = columns.get('default',False)
        self.permissions = columns.get('permissions',0)
        self.in_db = self._check_role()

    def _check_role(self):
        if self.id is not None:
            role_dict = self._check(self.tablename,'id',self.id)
        elif self.name is not None:
            role_dict = self._check(self.tablename,'name',self.name)
        else:
            logger.warning('No unique identifier was provided to check for role in database.')
            return False
        if role_dict is None:
            return False
        else:
            self.id = role_dict['id']
            self.name = role_dict['name']
            self.default = role_dict['default']
            self.permissions = role_dict['permissions']
            return True

    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0
    
    def has_permission(self,perm):
        return self.permissions & perm == perm
