# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
register = Declarations.register
Model = Declarations.Model
String = Declarations.Column.String
Json = Declarations.Column.Json
IOException = Declarations.Exception.IOException


@register(IOException)
class IOMappingCheckException(IOException):
    """ IO Exception for setter """


@register(IOException)
class IOMappingSetException(IOException):
    """ IO Exception for setter """


@register(Model.IO)
class Mapping:

    key = String(primary_key=True)
    model = String(primary_key=True,
                   foreign_key=(Model.System.Model, 'name'))
    primary_key = Json(nullable=False)

    @Declarations.hybrid_method
    def filter_by_model_and_key(self, model, key):
        """ SQLAlechemy hybrid method to filter by model and key

        :param model: model of the mapping
        :param key: external key of the mapping
        """
        return (self.model == model) & (self.key == key)

    @Declarations.hybrid_method
    def filter_by_model_and_keys(self, model, *keys):
        """ SQLAlechemy hybrid method to filter by model and key

        :param model: model of the mapping
        :param key: external key of the mapping
        """
        return (self.model == model) & self.key.in_(keys)

    @classmethod
    def multi_delete(cls, model, *keys):
        """ Delete all the keys for this model

        :param model: model of the mapping
        :param \*keys: list of the key
        :rtype: Boolean True if the mappings are removed
        """
        query = cls.query()
        query = query.filter(cls.filter_by_model_and_keys(model, *keys))
        if query.count():
            query.delete(synchronize_session='fetch')
            return True

        return False

    @classmethod
    def delete(cls, model, key):
        """ Delete the key for this model

        :param model: model of the mapping
        :param key: string of the key
        :rtype: Boolean True if the mapping is removed
        """
        query = cls.query()
        query = query.filter(cls.filter_by_model_and_key(model, key))
        if query.count():
            query.delete()
            return True

        return False

    @classmethod
    def get_primary_keys(cls, model, key):
        """ return primary key for a model and an external key

        :param model: model of the mapping
        :param key: string of the key
        :rtype: dict primary key: value or None
        """
        query = cls.query()
        query = query.filter(cls.filter_by_model_and_key(model, key))
        if query.count():
            pks = query.first().primary_key
            cls.check_primary_keys(model, *pks.keys())
            return pks

        return None

    @classmethod
    def check_primary_keys(cls, model, *pks):
        """ check if the all the primary keys match with primary keys of the
        model

        :param model: model to check
        :param pks: list of the primary keys to check
        :exception: IOMappingCheckException
        """
        for pk in cls.get_model(model).get_primary_keys():
            if pk not in pks:
                raise IOMappingCheckException(
                    "No primary key %r found in %r for model %r" % (
                        pk, pks, model))

    @classmethod
    def set_primary_keys(cls, model, key, pks, raiseifexist=True):
        """ Add or update a mmping with a model and a external key

        :param model: model to check
        :param key: string of the key
        :param pks: dict of the primary key to save
        :param raiseifexist: boolean (True by default), if True and the entry
            exist then an exception is raised
        :exception: IOMappingSetException
        """
        if cls.get_primary_keys(model, key):
            if raiseifexist:
                raise IOMappingSetException(
                    "One value found for model %r and key %r" % (model, key))
            cls.delete(model, key)

        if not pks:
            raise IOMappingSetException(
                "No value to save %r for model %r and key %r" % (
                    pks, model, key))

        cls.check_primary_keys(model, *pks.keys())
        return cls.insert(model=model, key=key, primary_key=pks)

    @classmethod
    def set(cls, key, instance, raiseifexist=True):
        """ Add or update a mmping with a model and a external key

        :param model: model to check
        :param key: string of the key
        :param instance: instance of the model to save
        :param raiseifexist: boolean (True by default), if True and the entry
            exist then an exception is raised
        :exception: IOMappingSetException
        """
        pks = instance.to_primary_keys()
        return cls.set_primary_keys(instance.__registry_name__, key, pks,
                                    raiseifexist=raiseifexist)

    @classmethod
    def get(cls, model, key):
        """ return instance of the model with this external key

        :param model: model of the mapping
        :param key: string of the key
        :rtype: instance of the model
        """
        pks = cls.get_primary_keys(model, key)
        if pks is None:
            return None

        return cls.get_model(model).from_primary_keys(**pks)
