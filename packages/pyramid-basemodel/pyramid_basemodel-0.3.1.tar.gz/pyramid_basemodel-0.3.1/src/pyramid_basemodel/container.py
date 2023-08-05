# -*- coding: utf-8 -*-

"""Provides a base model container, used by the Pyramid traversal
  machinery and a mixin to aid with traversal from an instance
  back up the tree.
"""

__all__ = [
    'BaseModelContainer',
    'InstanceTraversalMixin',
]

import logging
logger = logging.getLogger(__name__)

import re
valid_slug = re.compile(r'^[.\w-]{1,64}$', re.U)

from zope.interface import implementer
from zope.interface import alsoProvides

from sqlalchemy.exc import InvalidRequestError

from pyramid.interfaces import ILocation
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Deny
from pyramid.security import Authenticated, Everyone

from . import Session
from .interfaces import IModelContainer
from .root import BaseRoot

def slug_validator(node, value, regexp=None):
    """Default to using a slug regexp."""
    
    # Compose.
    if regexp is None:
        regexp = valid_slug
    
    # Raise a ValueError.
    if not regexp.match(value):
        raise ValueError(u'{0} is not a valid slug.'.format(value))


@implementer(IModelContainer)
class BaseModelContainer(BaseRoot):
    """Traversal factory that looks up model classes by property."""
    
    property_name = 'slug'
    validation_exception = Exception
    
    @property
    def _validator(self):
        return slug_validator
    
    
    # Default container acl to be private whilst granting authenticated
    # users create permission.
    __acl__ = [
        (Allow, 'r:admin', ALL_PERMISSIONS),
        (Allow, Authenticated, 'view'),
        (Allow, Authenticated, 'create'),
        (Deny, Everyone, ALL_PERMISSIONS),
    ]
    
    @property
    def name(self):
        return self.model_cls.plural_class_name
    
    @property
    def class_name(self):
        return self.model_cls.class_name
    
    @property
    def plural_class_name(self):
        return self.model_cls.plural_class_name
    
    @property
    def class_slug(self):
        return self.model_cls.class_slug
    
    def get_child(self, key):
        """Query for and return the child instance, if found."""
        
        column = getattr(self.model_cls, self.property_name)
        query = self.model_cls.query.filter(column==key)
        return query.first()
    
    def __getitem__(self, key):
        """Lookup model instance by key."""
        
        try:
            self.validator(None, key)
        except self.validation_exception:
            raise KeyError(key)
        
        context = self.get_child(key)
        if not context:
            raise KeyError(key)
        
        return self.locatable(context, key)
    
    def __init__(self, request, model_cls, key=None, parent=None, **kwargs):
        """Instantiate the container."""
        
        # Compose.
        if key is None:
            key = model_cls.class_slug
        if parent is None:
            parent = BaseRoot(request)
        
        self.request = request
        self.model_cls = model_cls
        self.__name__ = key
        self.__parent__ = parent
        if kwargs.has_key('property_name'):
            self.property_name = kwargs.get('property_name')
        if kwargs.has_key('validator'):
            self.validator = kwargs.get('validator')
        else:
            self.validator = self._validator
    

class InstanceTraversalMixin(object):
    """Provide a default __parent__ implementation for traversal."""
    
    request = None
    traversal_key_name = 'slug'
    validation_exception = Exception
    
    @property
    def _validator(self):
        return slug_validator
    
    @property
    def _base_child_query(self):
        return self.query
    
    
    def get_container(self):
        """Reverse up the parent traversal hierarchy until reaching a container."""
        
        target = self
        while True:
            parent = target.__parent__
            if not parent:
                return None
            if IModelContainer.providedBy(parent):
                return parent
            target = parent
    
    def locatable(self, context, key, provides=None):
        """Make a context object locatable and pass on the request."""
        
        # Compose.
        if provides is None:
            provides = alsoProvides
        
        if not hasattr(context, '__name__'):
            context.__name__ = key
        context._located_parent = self
        context.request = self.request
        if not ILocation.providedBy(context):
            provides(context, ILocation)
        return context
    
    
    @property
    def __parent__(self, container_cls=None, session=None):
        """Either return ``self.parent``, or a model container object."""
        
        # Compose.
        if container_cls is None:
            container_cls = BaseModelContainer
        if session is None:
            session = Session
        
        # If the context has been located, return the container.
        if hasattr(self, '_located_parent'):
            return self._located_parent
        
        # Add self to the session to avoid ``DetachedInstanceError``s.
        session.add(self)
        
        # If the model has a parent, return it.
        parent = getattr(self, 'parent', None)
        if parent:
            return parent
        
        # Otherwise instantiate a "fake" traversal container and return that.
        # It's "fake" because it doesn't know about it's parent and doesn't
        # have a copy of the request.
        container = container_cls(None, self.__class__)
        return container
    
    def __getitem__(self, key):
        """Lookup model instance by key."""
        
        try:
            self._validator(None, key)
        except self.validation_exception:
            raise KeyError(key)
        
        # Only lookup children from instances that have them.
        has_children = hasattr(self, 'children')
        if not has_children:
            raise KeyError(key)
        
        # Only lookup if the target column exists.
        column = getattr(self.__class__, self.traversal_key_name, None)
        if not column:
            raise KeyError(key)
        
        try:
            query = self._base_child_query
            query = query.filter_by(parent=self).filter(column==key)
            context = query.first()
            if not context:
                raise KeyError(key)
        except InvalidRequestError as err:
            # If the query was invalid, the lookup fails, e.g.: if the
            # instance had the requisit properties but they weren't actually
            # sqlalchemy columns.
            logger.warn(err, exc_info=True)
            raise KeyError(key)
        
        # Return the context, having set the parent and flagged as locatable.
        return self.locatable(context, key)
    

