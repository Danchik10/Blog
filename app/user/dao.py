from app.daos.base import BaseDao
from app.user.models import User, Role

class UserDAO(BaseDao):
    model = User

class RoleDAO(BaseDao):
    model = Role