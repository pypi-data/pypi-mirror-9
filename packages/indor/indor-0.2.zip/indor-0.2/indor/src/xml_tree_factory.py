__author__ = 'Bartek'

from singleton import Singleton


class XmlTreeFactory:
    __metaclass__ = Singleton

    def __init__(self):
        self.dict = {}

    def add_class(self, class_name, class_type):
        self.dict[class_name] = class_type

    def get_class(self, class_name):
        """t = contentType[:contentType.index(';')]
        t = t.split("/")
        class_name = ""
        for i in range(0,len(t)):
            class_name += t[i].lower().title()
        return self.dict[class_name]()"""
        return self.dict[class_name]()

# !!! Do not touch !!!
import xml_tree_register
import parsers_to_xml_tree
# !!! Do not touch !!!