"""Superclass module for all models."""
from datetime import datetime, timezone
from uuid import uuid4
# from sqlalchemy import Column, DateTime, String


class Superclass:
    """The BaseModel class from which future classes will be derived"""
    id = None
    created_at = None
    updated_at = None

    def __init__(self, **kwargs):
        self.id = str(uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __repr__(self):
        """Return the object representation."""
        return f"{self.__class__.__name__}: {self.id}"
