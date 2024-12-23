#!/usr/bin/env python

import json
import pickle


# -------------------------------------------------------------------------------------------------------- Shared Capabilities
# The callback method for nested objects. 
# Calls the callback method of its parent -> the callback bubbles up the tree
class ParentCaller():
    def __init__(self, parent, call_to_parent):
        self.parent = parent
        self.call_to_parent = call_to_parent

    def __call_from_child__(self, modified_object, modify_info, modify_trace):
        modify_trace.insert(0, self)
        self.parent.__call_from_child__(modified_object=modified_object, modify_info=modify_info, modify_trace=[self])

# Method to convert childs to NestedDict, NestedList or NestedTuple Class, 
# giving them the ability to convert nested objects and to call its parrent on data change
class ChildConverter():
    def __convert_child__(self, child):
        if isinstance(child, dict):
            # iter throu childs and convert them if they are a dict, a list, a tuble or a set
            for key, value in child.items():
                if isinstance(value, dict) or isinstance(value, list) or isinstance(value, tuple)  or isinstance(value, set):
                    child[key] = self.__convert_child__(value)
            # subclass the dict
            nestedDict = NestedDict(parent=self, call_to_parent=self.__call_from_child__)
            nestedDict.update(child)
            return nestedDict
        elif isinstance(child, list):
            # iter throu childs and convert them if they are a dict, a list, a tuble or a set
            for i in range(len(child)):
                if isinstance(child[i], dict) or isinstance(child[i], list) or isinstance(child[i], tuple)  or isinstance(child[i], set):
                    child[i] = self.__convert_child__(child[i])
            # subclass the list
            nestedList = NestedList(parent=self, call_to_parent=self.__call_from_child__)
            nestedList.extend(child)
            return nestedList
        elif isinstance(child, tuple):
            # iter throu childs and convert them if they are a dict, a list, a tuble or a set
            for i in range(len(child)):
                if isinstance(child[i], dict) or isinstance(child[i], list) or isinstance(child[i], tuple)  or isinstance(child[i], set):
                    child[i] = self.__convert_child__(child[i])
            # subclass the tuple
            nestedTuple = NestedTuple(parent=self, call_to_parent=self.__call_from_child__, iterable=child)
            return nestedTuple
        elif isinstance(child, set):
            # no need to iter throu the child items of the set, as they are not changable
            # subclass the set
            nestedSet = NestedSet(parent=self, call_to_parent=self.__call_from_child__, iterable=child)
            return nestedSet
        else:
            return child

# Custom update function for dicts
class DictUpdater():
    def update(self, *args, **kwargs):
        '''Update dict'''
        if args:
            if len(args) > 1:
                raise TypeError("update() expects at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

# Custom json encoder to encode non-serializable objects to binary strings
class Serializer(json.JSONEncoder):
    def __init__(self, serializer_hook, **kwargs):
        super(Serializer, self).__init__(**kwargs)
        self.serializer_hook = serializer_hook
    
    def default(self, obj):
        try:
            return {self.serializer_hook: pickle.dumps(obj).decode('latin-1')}
        except pickle.PickleError:
            return super().default(obj)


# -------------------------------------------------------------------------------------------------------- Nested Set Class
class NestedSet(set, ParentCaller):
    def __init__(self, parent, call_to_parent, iterable):
        ParentCaller.__init__(self, parent, call_to_parent)
        r = super(NestedSet, self).__init__(iterable)
        modify_info = {
            "type": type(self),
            "mode": "new",
            "iterable": iterable
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
    
    def __repr__(self):
        return str(set(self))
    
    def add(self, item):
        super(NestedSet, self).add(item)
        modify_info = {
            "type": type(self),
            "mode": "add",
            "item": item
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def update(self, iterable):
        super(NestedSet, self).update(iterable)
        modify_info = {
            "type": type(self),
            "mode": "update",
            "item": iterable
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def pop(self):
        r = super(NestedSet, self).pop()
        modify_info = {
            "type": type(self),
            "mode": "pop",
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
        
    def remove(self, item):
        super(NestedSet, self).remove(item)
        modify_info = {
            "type": type(self),
            "mode": "remove",
            "value": item
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def discard(self, item):
        super(NestedSet, self).discard(item)
        modify_info = {
            "type": type(self),
            "mode": "remove",
            "value": item
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def clear(self):
        super(NestedSet, self).clear()
        modify_info = {
            "type": type(self),
            "mode": "clear"
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])


# -------------------------------------------------------------------------------------------------------- Nested Tuple Class
class NestedTuple(tuple, ChildConverter, ParentCaller):
    def __init__(self, parent, call_to_parent, iterable):
        ParentCaller.__init__(self, parent, call_to_parent)
        
    def __new__ (self, parent, call_to_parent, iterable):
        ParentCaller.__init__(self, parent, call_to_parent)
        r = super(NestedTuple, self).__new__(self, iterable)
        modify_info = {
            "type": type(self),
            "mode": "new",
            "iterable": iterable
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r


# -------------------------------------------------------------------------------------------------------- Nested Dict Class
class NestedDict(dict, ChildConverter, ParentCaller, DictUpdater):
    def __init__(self, parent, call_to_parent):
        ParentCaller.__init__(self, parent, call_to_parent)

    def __setitem__(self, key, val):
        super(NestedDict, self).__setitem__(key, self.__convert_child__(val))
        modify_info = {
            "type": type(self),
            "mode": "setitem",
            "key": key,
            "value": val
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __delitem__(self, key):
        super(NestedDict, self).__delitem__(key)
        modify_info = {
            "type": type(self),
            "mode": "delitem",
            "key": key
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def clear(self):
        super(NestedDict, self).clear()
        modify_info = {
            "type": type(self),
            "mode": "clear"
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def pop(self, key):
        r = super(NestedDict, self).pop(key)
        modify_info = {
            "type": type(self),
            "mode": "pop",
            "key": key
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r

    def popitem(self, key):
        r = super(NestedDict, self).popitem(key)
        modify_info = {
            "type": type(self),
            "mode": "popitem",
            "key": key
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
    
    def setdefault(self, key, default=None):
        r = super(NestedDict, self).setdefault(key, default=default)
        modify_info = {
            "type": type(self),
            "mode": "setdefault",
            "key": key,
            "default": default
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r

    def update(self, *args, **kwargs):
        DictUpdater.update(self, *args, **kwargs)


# -------------------------------------------------------------------------------------------------------- Nested List Class
class NestedList(list, ChildConverter, ParentCaller):
    def __init__(self, parent, call_to_parent):
        ParentCaller.__init__(self, parent, call_to_parent)

    def __add__(self, item):
        super(NestedList, self).__add__(item)
        modify_info = {
            "type": type(self),
            "mode": "add",
            "item": item
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __delitem__(self, index):
        super(NestedList, self).__delitem__(index)
        modify_info = {
            "type": type(self),
            "mode": "delitem",
            "index": index
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __delslice__(self, i, j):
        super(NestedList, self).__delslice__(i, j)
        modify_info = {
            "type": type(self),
            "mode": "delslice",
            "start": i,
            "end": j
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __setitem__(self, index, value):
        super(NestedList, self).__setitem__(index, self.__convert_child__(value))
        modify_info = {
            "type": type(self),
            "mode": "setitem",
            "index": index,
            "value": value
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def __setslice__(self, i, j, y):
        super(NestedList, self).__setslice__(i, j, y)
        modify_info = {
            "type": type(self),
            "mode": "setsclice",
            "start": i,
            "end": j,
            "item": y
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def append(self, obj):
        '''L.append(object) -- append object to end'''
        super(NestedList, self).append(self.__convert_child__(obj))
        modify_info = {
            "type": type(self),
            "mode": "append",
            "item": obj
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def extend(self, iterable):
        '''L.extend(iterable) -- extend list by appending elements from the iterable'''
        for item in iterable:
            self.append(self.__convert_child__(item))
        modify_info = {
            "type": type(self),
            "mode": "extend",
            "iterable": iterable
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def insert(self, index, item):
        '''L.insert(index, object) -- insert object before index'''
        super(NestedList, self).insert(index, self.__convert_child__(item))
        modify_info = {
            "type": type(self),
            "mode": "insert",
            "index": index,
            "item": item
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def pop(self, index=-1):
        '''L.pop([index]) -> item -- remove and return item at index (default last).
        Raises IndexError if list is empty or index is out of range.'''
        r = super(NestedList, self).pop(index)
        modify_info = {
            "type": type(self),
            "mode": "pop",
            "index": index
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
        
    def remove(self, value):
        '''L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present.'''
        super(NestedList, self).remove(value)
        modify_info = {
            "type": type(self),
            "mode": "remove",
            "value": value
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def clear(self):
        super(NestedList, self).clear()
        modify_info = {
            "type": type(self),
            "mode": "clear"
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def reverse(self):
        '''L.reverse() -- reverse *IN PLACE*'''
        super(NestedList, self).reverse()
        modify_info = {
            "type": type(self),
            "mode": "reverse",
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def sort(self, key=None, reverse=False):
        '''L.sort(cmp=None, key=None, reverse=False) -- stable sort *IN PLACE*;
        cmp(x, y) -> -1, 0, 1'''
        super(NestedList, self).sort(key=key, reverse=reverse)
        modify_info = {
            "type": type(self),
            "mode": "sort",
            "key": key,
            "reverse": reverse
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])