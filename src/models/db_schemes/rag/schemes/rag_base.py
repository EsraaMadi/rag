# Importing the declarative_base function from SQLAlchemy's extension module.
# This function is used to create a base class for declarative class definitions.
from sqlalchemy.ext.declarative import declarative_base

# Creating a base class for all ORM models to inherit from.
# This base class contains metadata and functionality shared by all model classes.
SQLAlchemyBase = declarative_base()
