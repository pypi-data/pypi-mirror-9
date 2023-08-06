from copy import copy
from collections import OrderedDict
from abc import ABCMeta

class SkipMark(Exception):
    pass

class Mark(metaclass=ABCMeta):

    collect_into = '_declared_marks'

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def build(self, marks, owner):
        # can raise SkipMark
        return self


class DeclaredMeta(type):
    '''
    The metaclass collects `Mark` instances from the classdict
    and then removes from the class namespace.
    '''

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    def __new__(cls, name, bases, namespace):
        marks_dict = OrderedDict()
        for key, obj in namespace.items():
            if not isinstance(obj, Mark):
                continue
            # make clones if necessary so that all marks
            # were different objects
            if obj in marks_dict.values():
                obj = copy(obj)
            marks_dict[key] = obj

        # clear the namespace
        for _name in marks_dict:
            del namespace[_name]

        is_lazy = any(isinstance(mark, declare) for mark in marks_dict.values())

        if is_lazy:
            def process_declared(self):
                return cls.process_declared(self, marks_dict)

            namespace['process_declared'] = process_declared

        klass = type.__new__(cls, name, bases, namespace)
        if not is_lazy:
            cls.process_declared(klass, marks_dict)

        return klass

    @classmethod
    def process_declared(cls, owner, marks_dict):
        all_marks = list(marks_dict.values())
        created_attrs = set() # TODO write comments
        for key, mark in marks_dict.items():
            # if not isinstance(owner, type):
            if Mark in mark.__class__.__mro__:
                mark_type = mark.__class__
            else:
                mark_type = getattr(owner, 'default_mark', Mark)
            try:
                # build mark
                build = mark_type.build(mark, all_marks, owner)
            except SkipMark:
                continue
            collect_into = mark_type.collect_into # where to store mark
            if callable(collect_into):
                collect_into = collect_into(mark)

            if collect_into not in created_attrs:
                created_attrs.add(collect_into)
                setattr(owner, collect_into, OrderedDict([(key, build)]))
            else:
                getattr(owner, collect_into)[key] = build


class declare(Mark):
    '''Lazy declaration.'''

    func = None

    def collect_into(self):
        mark = self.evaluated
        if self.mark_type:
            mark_type = self.mark_type
        elif Mark in mark.__class__.__mro__:
            mark_type = mark.__class__
        else:
            mark_type = getattr(self.owner, 'default_mark', Mark)
        collect_into = mark_type.collect_into # where to store mark
        if callable(collect_into):
            return collect_into(mark)
        return collect_into

    def build(self, marks, owner):
        self.evaluated = self.func(owner)
        self.owner = owner
        if self.mark_type:
            return self.mark_type.build(self.evaluated, marks, owner)
        return self.evaluated

    def __init__(self, mark_type=None):
        self.mark_type = mark_type

    def __call__(self, func):
        self.func = func
        return self

class Declared(metaclass=DeclaredMeta):
    pass
