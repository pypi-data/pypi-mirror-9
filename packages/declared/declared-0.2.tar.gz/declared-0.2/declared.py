from copy import copy
from collections import OrderedDict
from abc import ABCMeta

class SkipMark(Exception):
    pass

class Mark(metaclass=ABCMeta):

    collect_into = '_declared_marks'

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    @classmethod
    def build(cls, mark, owner, marks_dict):
        # can raise SkipMark
        return mark


class lazy(metaclass=ABCMeta):

    def __init__(self, func):
        self.func = func


class DeclaredMeta(type):
    '''
    The metaclass collects `Mark` instances from the classdict
    and then removes from the class namespace.
    '''

    mark_type = Mark

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    @property
    def mark_type(cls):
        return cls.process_declared.mark_type

    def __new__(cls, name, bases, namespace, extract=None):
        for base in bases:
            if extract:
                break
            extract = getattr(base, 'mark_type', None)
        else:
            extract = extract or Mark
        marks_dict = OrderedDict()
        for key, obj in namespace.items():
            if not isinstance(obj, (extract, lazy)):
                continue
            # make clones if necessary so that all marks
            # were different objects
            if obj in marks_dict.values():
                obj = copy(obj)
            marks_dict[key] = obj

        namespace['process_declared'] = ProcessDeclared(marks_dict, extract)

        return super().__new__(cls, name, bases, namespace)


    def __init__(cls, *args, extract=None):
        if not cls.process_declared.lazy:
            cls.process_declared()
        return super().__init__(*args)


class ProcessDeclared:

    def __init__(self, marks_dict, mark_type,  owner=None):
        self.marks_dict = marks_dict
        self.mark_type = mark_type
        self.owner = owner

    def __get__(self, instance, klass):
        return self.__class__(self.marks_dict, self.mark_type,
                              instance or klass)

    def __call__(self):
        for key in self.lazy:
            self.marks_dict[key] = self.marks_dict[key].func(self.owner)
        collect_into = self.mark_type.collect_into
        setattr(self.owner, collect_into, OrderedDict())
        for key, mark in self.marks_dict.items():
            try:
                built = self.mark_type.build(mark, self.owner, self.marks_dict)
            except SkipMark:
                continue
            setattr(self.owner, key, built)
            getattr(self.owner, collect_into)[key] = built

    @property
    def lazy(self):
        return tuple(k for k, v in self.marks_dict.items()
                     if isinstance(v, lazy))


class Declared(metaclass=DeclaredMeta):
    pass
