from .config import CRUD

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