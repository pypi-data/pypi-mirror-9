# -*- coding: utf-8 -*-

'''File metadata storage backend base class using SQLAlchemy.

    This class certainly needs to be subclassed for your specific use case.
    You must examine the source code and override methods as necessary.
    The most important reason for this is that each application will need
    to namespace the stored files differently.

    Configuration settings
    ======================

    - ``sql.file_model_cls`` must point to a certain model class to store
      the file metadata.
    - ``sql.session`` should point to a scoped session global variable.
      But instead of using this setting, you may override the
      ``_get_session()`` method.

    Creating your File model class
    ==============================

    Your File model class must inherit from the BaseFile mixin class that
    we provide. Here is an example in which files are separated by user::

        from bag import fk_rel
        from keepluggable.storage_metadata.sql import (
            BaseFile, SQLAlchemyMetadataStorage)
        from sqlalchemy import Column, UniqueConstraint
        from sqlalchemy.types import Unicode

        from myapp.db import Base
        from myapp.modules.user.models import User


        class File(Base, BaseFile):
            __table_args__ = (
                UniqueConstraint('user_id', 'md5', name='file_user_md5_key'),
                {})

            # You can add any columns for information entered by the user:
            description = Column(Unicode(320), nullable=False, default='')
            # title = Column(Unicode(80), nullable=False)
            # alt

            # Relationships
            user_id, user = fk_rel(User, backref='files')

            @property  # Your File model must define a "namespace" property.
            def namespace(self):  # In this example a user has her own files.
                return str(self.user_id)

        # Create a self-referential foreign key and relationship so that
        # a file can point to its original version:
        File.original_id, File.versions = fk_rel(File, nullable=True)
        # When original_id is null, this is the original file.
    '''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from bag.sqlalchemy.tricks import ID, MinimalBase, now_column
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode
from keepluggable import resolve_setting


class SQLAlchemyMetadataStorage(object):
    __doc__ = __doc__

    def __init__(self, settings):
        self.settings = settings

        self.file_model_cls = resolve_setting(
            self.settings, 'sql.file_model_cls')

        # Instantiate a session at startup just to make sure it is configured
        self._get_session()

    def _get_session(self):
        '''Returns the SQLAlchemy session.'''
        return resolve_setting(self.settings, 'sql.session')

    def put(self, namespace, metadata, sas=None):
        '''Create or update a file corresponding to the given ``metadata``.
            This method returns a 2-tuple containing the ID of the entity
            and a boolean saying whether the entity is new or existing.

            Instead of overriding this method, it is probably better for
            you to override the methods it calls.
            '''
        sas = sas or self._get_session()
        entity = self._query(namespace, key=metadata['md5'], sas=sas).first()
        is_new = entity is None
        if is_new:
            entity = self._instantiate(namespace, metadata, sas=sas)
            sas.add(entity)
        else:
            self._update(namespace, metadata, entity, sas=sas)
        sas.flush()
        return entity.id, is_new

    def _query(self, namespace, key=None, filters=None, what=None, sas=None):
        '''Override this to search for an existing file.
            You probably need to do something with the ``namespace``.
            '''
        sas = sas or self._get_session()
        q = sas.query(what or self.file_model_cls)
        if key is not None:
            q = q.filter_by(md5=key)
        if filters is not None:
            q = q.filter_by(**filters)
        return q

    def _instantiate(self, namespace, metadata, sas=None):
        '''Override this to add or delete arguments on the constructor call.
            You probably need to do something with the ``namespace``.
            '''
        return self.file_model_cls(**metadata)

    def _update(self, namespace, metadata, entity, sas=None):
        '''Override this to update the metadata of an existing entity.
            You might need to do something with the ``namespace``.
            '''
        for key, value in metadata.items():
            setattr(entity, key, value)

    def update(self, namespace, id, metadata, sas=None):
        '''Updates a file metadata. It must already exist in the database.'''
        sas = sas or self._get_session()
        # entity = self._query(namespace, key=key, sas=sas).one()
        # entity = self._query(namespace, sas=sas).get(id)
        entity = sas.query(self.file_model_cls).get(id)
        self._update(namespace, metadata, entity, sas=sas)
        sas.flush()
        return entity.to_dict()

    def gen_originals(self, namespace, filters=None, sas=None):
        filters = {} if filters is None else filters
        filters['version'] = 'original'
        for entity in self._query(namespace, filters=filters, sas=sas):
            yield entity.to_dict()

    # Not currently used, except by the local storage
    def gen_keys(self, namespace, filters=None, sas=None):
        '''Generator of the keys in a namespace.'''
        sas = sas or self._get_session()
        q = self._query(
            namespace, filters=filters, what=self.file_model_cls.md5, sas=sas)
        for tup in q:
            yield tup[0]

    def get(self, namespace, key, sas=None):
        '''Returns a dict containing the metadata of one file,
            or None if not found.
            '''
        sas = sas or self._get_session()
        entity = self._query(sas=sas, namespace=namespace, key=key).first()
        return entity.to_dict() if entity else None

    def delete_with_versions(self, namespace, key, sas=None):
        '''Delete a file along with all its versions.'''
        sas = sas or self._get_session()
        original = self._query(
            sas=sas, namespace=namespace, key=key).one()
        for version in original.versions:
            sas.delete(version)
        sas.delete(original)

    def delete(self, namespace, key, sas=None):
        '''Delete one file.'''
        sas = sas or self._get_session()
        self._query(sas=sas, namespace=namespace, key=key).delete()


class BaseFile(ID, MinimalBase):
    '''Base mixin class for a model that represents file metadata.
        The file MAY be an image.
        '''
    # id = Primary key that exists because we inherit from ID
    md5 = Column(Unicode(32), nullable=False,
                 doc='hashlib.md5(file_content).hexdigest()')
    file_name = Column(Unicode(300))  # includes the file_extension
    length = Column(Integer, nullable=False, doc='File size in bytes')
    created = now_column()  # Stores the moment the instance is created
    mime_type = Column(Unicode(40), doc='MIME type; e.g. "image/jpeg"')
    image_width = Column(Integer, doc='Image width in pixels')
    image_height = Column(Integer, doc='Image height in pixels')
    image_format = Column(Unicode(20), doc='JPEG, PNG, GIF etc.')
    version = Column(Unicode(20), default='original')

    @property
    def is_image(self):
        return self.image_width is not None

    @property
    def aspect_ratio(self):
        return self.image_width / self.image_height

    @property
    def is_the_original(self):
        return self.original_id is None

    def get_original(self, sas):
        return sas.query(type(self)).get(self.original_id)

    def q_versions(self, sas, order_by=created):
        return sas.query(type(self)).filter_by(
            original=self).order_by(order_by)

    def __repr__(self):
        return '<{} #{} "{}" {}>'.format(
            type(self).__name__, self.id, self.file_name, self.version)

    def to_dict(self, versions=True):
        '''Convert this File, and optionally its versions, to a dictionary.'''
        d = super(BaseFile, self).to_dict()
        if versions:
            d['versions'] = []
            for version in self.versions:
                d['versions'].append(version.to_dict())
        return d
