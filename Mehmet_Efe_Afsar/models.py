from pyasn1.compat import integer

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Recipe(Base):
    __tablename__ = 'Recipes'

    id = Column(Integer, primary_key=True, index=True)
    recipe_title = Column(String)
    description = Column(String)
    carbon_footprint = Column(String)
    ingredients = Column(String)
    calories = Column(Integer)
    owner_id = Column(Integer, ForeignKey('users.id'))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    tree_level = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)