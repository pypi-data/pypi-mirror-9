# coding: utf-8
"""
:mod:`boardgamegeek.user` - Generic objects
===========================================

.. module:: boardgamegeek.user
   :platform: Unix, Windows
   :synopsis: Generic objects

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>

"""
from __future__ import unicode_literals

from .exceptions import BoardGameGeekError
from .utils import DictObject


class Thing(DictObject):
    """
    A thing, an object with a name and an id
    """
    def __init__(self, data):
        for i in ["id", "name"]:
            if i not in data:
                raise BoardGameGeekError("missing '{}' when trying to create a Thing".format(i))

        try:
            data["id"] = int(data["id"])
        except:
            raise BoardGameGeekError("id ({}) is not an int when trying to create a Thing".format(data["id"]))

        super(Thing, self).__init__(data)

    @property
    def name(self):
        return self._data["name"]

    @property
    def id(self):
        return self._data["id"]

    def __repr__(self):
        return "Thing (id: {})".format(self.id)