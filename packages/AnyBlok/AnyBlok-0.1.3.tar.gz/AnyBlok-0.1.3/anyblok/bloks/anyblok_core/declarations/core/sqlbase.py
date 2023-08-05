# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from sqlalchemy.orm import aliased


@Declarations.register(Declarations.Exception)
class SqlBaseException(Exception):
    """ Simple Exception for sql base """


def query_method(name):
    """ Apply a wrapper on a method name and return the classmethod of
    wrapper for this name
    """

    def wrapper(cls, query, *args, **kwargs):
        return query.sqlalchemy_query_method(name, *args, **kwargs)

    return classmethod(wrapper)


class SqlMixin:

    @classmethod
    def query(cls, *elements):
        """ Facility to do a SqlAlchemy query::

            query = MyModel.query()

        is equal at::

            query = self.registry.session.query(MyModel)

        :param elements: pass at the SqlAlchemy query, if the element is a
        string then thet are see as field of the model
        :rtype: SqlAlchemy Query
        """
        res = []
        for f in elements:
            if isinstance(f, str):
                res.append(getattr(cls, f))
            else:
                res.append(f)

        if res:
            return cls.registry.query(*res)

        return cls.registry.query(cls)

    is_sql = True

    @classmethod
    def get_on_model_methods(cls):
        return ['update', 'delete']

    @classmethod
    def aliased(cls, *args, **kwargs):
        """ Facility to Apply an aliased on the model::

            MyModelAliased = MyModel.aliased()

        is equal at::

            from sqlalchemy.orm import aliased
            MyModelAliased = aliased(MyModel)

        :rtype: SqlAlchemy aliased of the model
        """
        return aliased(cls, *args, **kwargs)


@Declarations.register(Declarations.Core)
class SqlBase(SqlMixin):
    """ this class is inherited by all the SQL model
    """

    sqlalchemy_query_delete = query_method('delete')
    sqlalchemy_query_update = query_method('update')

    def update(self, *args, **kwargs):
        """ Call the SqlAlchemy Query.update method on the model::

            self.update({...})

        is equal at::

            query = self.registry.session.query(MyModel)
            query = query.filter(MyModel.``pk`` == self.``pk``)
            query.update({...})

        """
        pks = [c.name for c in self.__table__.primary_key.columns.values()]
        where_clause = [getattr(self.__class__, pk) == getattr(self, pk)
                        for pk in pks]
        self.__class__.query().filter(*where_clause).update(*args, **kwargs)

    @classmethod
    def insert(cls, **kwargs):
        """ Insert in the table of the model::

            MyModel.insert(...)

        is equal at::

            mymodel = MyModel(...)
            MyModel.registry.session.add(mymodel)
            MyModel.registry.session.flush()

        """
        instance = cls(**kwargs)
        cls.registry.add(instance)
        cls.registry.flush()
        return instance

    @classmethod
    def multi_insert(cls, *args):
        """ Insert in the table one or more entry of the model::

            MyModel.multi_insert([{...}, ...])

        the flush will be done only one time at the end of the insert

        :exception: SqlBaseException
        """
        instances = []
        for kwargs in args:
            if not isinstance(kwargs, dict):
                raise SqlBaseException("inserts method wait list of dict")

            instance = cls(**kwargs)
            cls.registry.add(instance)
            instances.append(instance)

        if instances:
            cls.registry.flush()

        return instances

    @classmethod
    def precommit_hook(cls, method, put_at_the_end_if_exist=False):
        """ Same in the registry a hook to call just before the commit

        .. warning:: Only one instance of the hook is called before the commit

        :param method: the method to call on this model
        put_at_the_end_if_exist: If ``True`` the hook is move at the end
        """
        cls.registry.precommit_hook(cls.__registry_name__, method,
                                    put_at_the_end_if_exist)
