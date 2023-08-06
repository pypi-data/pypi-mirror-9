#!/usr/bin/env python

# Copyright 2010 Louis Paternault

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This file define the Enum class
"""

class Enum:
    """
    This class implements an enumeration type, with elements that can be
    compared to each other, but whose value is irrelevant.

    Once a name has been registered (using the constructor, or
    self.__register__(name)), it can be accessed by self.name.
    User is assured that each name (of a same Enum instance) has a
    different value.
    """
    def __init__(self, *args):
        """
        Arguments:
        - *args: list of names for items of the enumeration.
        """
        self.__next = 0
        self.__items = {}
        self.__reverse_items = {}
        self._type = type(self.__next)
        for i in args:
            self.__register__(i)

    def __register__(self, name, value = None):
        """
        Register a name. It can be later accessed by self.name.
        Argument:
            - name: the name. It must be a non-empty string, must not begin
              with an underscore, and must be different from every other
              name of this instance. It should be a name accepted as a name for
              a Python method, but no check is done on that.
            - value: the value associated with this name. If value is None,
              self.__next is given, and self.__next is incremented. If another
              value is given, it is associated to the name.
        Return:
            nothing
        Postconditions:
            - value is different from every other value of this instance.
        Raise exceptions when:
            - some of the condition of the argument is not met.
        """
        if (type("") != type(name)):
            raise Exception("Name must be a string.")
        if (self.__items.has_key(name)):
            raise Exception("Name \"%s\" already exists." % name)
        if (name[0:1] == "_"):
            raise Exception("Name cannot begin with \"__\".")
        if (value == None):
            while(self.__reverse_items.has_key(self.__next)):
                self.__next += 1
            self.__items[name] = self.__next
            self.__reverse_items[self.__next] = name
            self.__next += 1
        else:
            if (self.__reverse_items.has_key(value)):
                raise Exception(
                        "Error: value %s is already taken." % str(value))
            self.__items[name] = value
            self.__reverse_items[value] = name

    def __enum_type__(self):
        """
        Return the type of values of type
        """
        return type(self.__next)

    def __names__(self):
        """
        Return the list of registered names
        """
        return self.__items.keys()

    def __enum_name__(self, value):
        """
        Return the name having "value" as its value.
        """
        return self.__reverse_items[value]

    def __getattr__(self, name):
        if (not self.__items.has_key(name)):
            raise Exception("Name \"%s\" does not exist." % name)
        else:
            return self.__items[name]

    def __str__(self):
        return ', '.join(['%s: %s' % (str(k), str(v))
            for k, v in self.__items.items()])
