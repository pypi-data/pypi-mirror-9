# coding: utf-8

from __future__ import unicode_literals
from six import add_metaclass
from boxsdk.util.singleton import Singleton


@add_metaclass(Singleton)
class Translator(object):
    """
    Translate item responses from the Box API to Box objects.
    """
    def __init__(self):
        self._type_to_class_mapping = {}

    def register(self, type_name, box_cls):
        """
        Associate a box object class to handle Box API item responses with the given type name.
        """
        self._type_to_class_mapping.update({
            type_name: box_cls,
        })

    def translate(self, type_name):
        """
        Get the box object class associated with the given type name.
        """
        return self._type_to_class_mapping.get(type_name, None)
