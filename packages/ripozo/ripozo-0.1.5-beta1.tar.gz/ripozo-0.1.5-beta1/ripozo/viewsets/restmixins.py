from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'
import logging
from ripozo.decorators import apimethod
from ripozo.viewsets.fields.base import translate_and_validate_fields, translate_fields
from ripozo.viewsets.resource_base import ResourceBase

logger = logging.getLogger(__name__)

# TODO documentation


class Create(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['POST'])
    def create(cls, primary_keys, filters, values, *args, **kwargs):
        logger.info('Creating a model for resource {0}'.format(cls.resource_name))
        primary_keys, filters, values = translate_and_validate_fields(primary_keys, filters, values,
                                                                      fields=cls.manager.field_validators)
        obj = cls.manager.create(values, *args, **kwargs)
        return cls(properties=obj)


class RetrieveList(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    def retrieve_list(cls, primary_keys, filters, values, *args, **kwargs):
        logger.info('Retrieving a list of models for resource {0} '
                    'with filters {1}'.format(cls.resource_name, filters))
        primary_keys, filters, values = translate_fields(primary_keys, filters, values,
                                                         fields=cls.manager.field_validators)
        results, next_query_args = cls.manager.retrieve_list(filters, *args, **kwargs)
        results = dict(objects=results)
        results.update(next_query_args)
        return cls(properties=results)


class RetrieveSingle(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    def retrieve(cls, primary_keys, filters, values, *args, **kwargs):
        logger.info('Retrieving a model for resource {0}'
                    'with primary keys {0}'.format(cls.resource_name, primary_keys))
        primary_keys, filters, values = translate_fields(primary_keys, filters, values,
                                                         fields=cls.manager.field_validators)
        obj = cls.manager.retrieve(primary_keys, *args, **kwargs)
        return cls(properties=obj)


class Update(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['PATCH'])
    def update(cls, primary_keys, filters, values, *args, **kwargs):
        logger.info('Updating a model for resource {0}'
                    'with primary keys'.format(cls.resource_name, primary_keys))
        primary_keys, filters, values = translate_fields(primary_keys, filters, values,
                                                         fields=cls.manager.field_validators)
        obj = cls.manager.update(primary_keys, values, *args, **kwargs)
        return cls(properties=obj)


class Delete(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['DELETE'])
    def remove(cls, primary_keys, filters, values, *args, **kwargs):
        logger.info('Deleting a model for resource {0}'
                    'with primary keys'.format(cls.resource_name, primary_keys))
        primary_keys, filters, values = translate_fields(primary_keys, filters, values,
                                                         fields=cls.manager.field_validators)
        cls.manager.delete(primary_keys, *args, **kwargs)
        return cls()
