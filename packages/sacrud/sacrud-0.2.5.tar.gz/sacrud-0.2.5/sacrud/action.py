#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
CREATE, READ, DELETE, UPDATE actions for SQLAlchemy models
"""
import transaction

from .common import get_obj, get_obj_by_request
from .preprocessing import ObjPreprocessing


class CRUD(object):

    """ Main class for CRUD actions

        :Parameters:

            - `session`: SQLAlchemy DBSession
            - `table`: SQLAlchemy model
            - `commit`: To do or not after modify object
            - `preprocessing`: you custom preprocessing class
    """

    def __init__(self, session, table, preprocessing=ObjPreprocessing,
                 commit=True):
        self.table = table
        self.session = session
        self.commit = commit
        self.preprocessing = preprocessing

    def create(self, data, **kwargs):
        """
        Creates a new object pretreated input data.

        .. code-block:: python

            DBSession.sacrud(Users).create({'name': 'Vasya', 'sex': 1})

        For adding multiple data for m2m or m2o use endinng `[]`, ex.:

        .. code-block:: python

            DBSession.sacrud(Users).create(
                {'name': 'Vasya', 'sex': 1,
                 'groups[]': ['["id", 1]', '["id", 2]']}
            )
        """
        obj = get_obj_by_request(self.session, self.table, data)
        return self._add(obj, data, **kwargs)

    def read(self, *pk):
        """
        Return a list of entries in the table or single
        entry if there is an pk.

        .. code-block:: python

            # All users
            DBSession.sacrud(Users).read()

            # Composite primary_key
            DBSession.sacrud(User2Groups).read({'user_id': 4, 'group_id': 2})
            DBSession.sacrud(User2Groups).read(
              pk=[{'user_id': 4, 'group_id': 2},
                  {'user_id': 4, 'group_id': 3},
                  {'user_id': 1, 'group_id': 1},
                  {'user_id': 19, 'group_id': 2}]
             )

            # Same, but work with only not composite primary key
            DBSession.sacrud(Users).read((5, 10))   # as list
            DBSession.sacrud(Users).read(5, "1", 2) # as *args
            DBSession.sacrud(Users).read(42)        # single
        """

        if len(pk) == 1:  # like ([1,2,3,4,5], )
            return get_obj(self.session, self.table, pk[0])
        elif len(pk) > 1:  # like (1, 2, 3, 4, 5)
            return get_obj(self.session, self.table, pk)
        return self.session.query(self.table)

    def update(self, pk, data, **kwargs):
        """
        Updates the object by primary_key.

        .. code-block:: python

            DBSession.sacrud(Users).update(1, {'name': 'Petya'})
            DBSession.sacrud(Users).update('1', {'name': 'Petya'})
            DBSession.sacrud(User2Groups).update({'user_id': 4, 'group_id': 2},
                                                 {'group_id': 1})

        Default it run ``session.commit() or transaction.commit()``.
        If it is not necessary use attribute ``commit=False``.
        """
        obj = get_obj(self.session, self.table, pk)
        return self._add(obj, data, **kwargs)

    def delete(self, pk, **kwargs):
        """
        Delete the object by primary_key.

        .. code-block:: python

            DBSession.sacrud(Users).delete(1)
            DBSession.sacrud(Users).delete('1')
            DBSession.sacrud(User2Groups).delete({'user_id': 4, 'group_id': 2})

        Default it run ``session.commit() or transaction.commit()``.
        If it is not necessary use attribute ``commit=False``.
        """
        obj = get_obj(self.session, self.table, pk)
        if self._delete(obj, **kwargs):
            return {'pk': pk, 'name': obj.__repr__()}

    def _add(self, obj, data, **kwargs):
        """ Update the object directly.

        .. code-block:: python

            DBSession.sacrud(Users)._add(UserObj, {'name': 'Gennady'})
        """
        obj = self.preprocessing(obj=obj or self.table)\
            .add(self.session, data, self.table)
        self.session.add(obj)
        if kwargs.get('commit', self.commit) is True:
            try:
                self.session.commit()
            except AssertionError:
                transaction.commit()
        return obj

    def _delete(self, obj, **kwargs):
        """ Delete the object directly.

        .. code-block:: python

            DBSession.sacrud(Users)._delete(UserObj)

        If you no needed commit session

        .. code-block:: python

            DBSession.sacrud(Users, commit=False)._delete(UserObj)
        """
        obj = self.preprocessing(obj=obj).delete()
        self.session.delete(obj)
        if kwargs.get('commit', self.commit) is True:
            try:
                self.session.commit()
            except AssertionError:
                transaction.commit()
        return True
