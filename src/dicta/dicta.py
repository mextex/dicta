#!/usr/bin/env python

import os
import re
import pickle
import json
import inspect

default_serializer_hook = "<serialized_object>"

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
        previous_object = self.copy()
        ParentCaller.__init__(self, parent, call_to_parent)
        r = super(NestedSet, self).__init__(iterable)
        modify_info = {
            "type": type(self),
            "mode": "new",
            "iterable": iterable,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
    
    def __repr__(self):
        return str(set(self))
    
    def add(self, item):
        previous_object = self.copy()
        super(NestedSet, self).add(item)
        modify_info = {
            "type": type(self),
            "mode": "add",
            "item": item,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def update(self, iterable):
        previous_object = self.copy()
        super(NestedSet, self).update(iterable)
        modify_info = {
            "type": type(self),
            "mode": "update",
            "item": iterable,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def pop(self):
        previous_object = self.copy()
        r = super(NestedSet, self).pop()
        modify_info = {
            "type": type(self),
            "mode": "pop",
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
        
    def remove(self, item):
        previous_object = self.copy()
        super(NestedSet, self).remove(item)
        modify_info = {
            "type": type(self),
            "mode": "remove",
            "value": item,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def discard(self, item):
        previous_object = self.copy()
        super(NestedSet, self).discard(item)
        modify_info = {
            "type": type(self),
            "mode": "remove",
            "value": item,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def clear(self):
        previous_object = self.copy()
        super(NestedSet, self).clear()
        modify_info = {
            "type": type(self),
            "mode": "clear",
            "modified_object": self,
            "previous_object": previous_object
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
            "iterable": iterable,
            "modified_object": self
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r


# -------------------------------------------------------------------------------------------------------- Nested Dict Class
class NestedDict(dict, ChildConverter, ParentCaller, DictUpdater):
    def __init__(self, parent, call_to_parent):
        ParentCaller.__init__(self, parent, call_to_parent)

    def __setitem__(self, key, val):
        previous_object = self.copy()
        super(NestedDict, self).__setitem__(key, self.__convert_child__(val))
        modify_info = {
            "type": type(self),
            "mode": "setitem",
            "key": key,
            "value": val,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __delitem__(self, key):
        previous_object = self.copy()
        super(NestedDict, self).__delitem__(key)
        modify_info = {
            "type": type(self),
            "mode": "delitem",
            "key": key,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def clear(self):
        previous_object = self.copy()
        super(NestedDict, self).clear()
        modify_info = {
            "type": type(self),
            "mode": "clear",
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def pop(self, key):
        previous_object = self.copy()
        r = super(NestedDict, self).pop(key)
        modify_info = {
            "type": type(self),
            "mode": "pop",
            "key": key,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r

    def popitem(self, key):
        previous_object = self.copy()
        r = super(NestedDict, self).popitem(key)
        modify_info = {
            "type": type(self),
            "mode": "popitem",
            "key": key,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
    
    def setdefault(self, key, default=None):
        previous_object = self.copy()
        r = super(NestedDict, self).setdefault(key, default=default)
        modify_info = {
            "type": type(self),
            "mode": "setdefault",
            "key": key,
            "default": default,
            "modified_object": self,
            "previous_object": previous_object
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
        previous_object = self.copy()
        super(NestedList, self).__add__(item)
        modify_info = {
            "type": type(self),
            "mode": "add",
            "item": item,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __delitem__(self, index):
        previous_object = self.copy()
        super(NestedList, self).__delitem__(index)
        modify_info = {
            "type": type(self),
            "mode": "delitem",
            "index": index,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __delslice__(self, i, j):
        previous_object = self.copy()
        super(NestedList, self).__delslice__(i, j)
        modify_info = {
            "type": type(self),
            "mode": "delslice",
            "start": i,
            "end": j,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

    def __setitem__(self, index, value):
        previous_object = self.copy()
        super(NestedList, self).__setitem__(index, self.__convert_child__(value))
        modify_info = {
            "type": type(self),
            "mode": "setitem",
            "index": index,
            "value": value,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def __setslice__(self, i, j, y):
        previous_object = self.copy()
        super(NestedList, self).__setslice__(i, j, y)
        modify_info = {
            "type": type(self),
            "mode": "setsclice",
            "start": i,
            "end": j,
            "sequence": y,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def append(self, obj):
        '''L.append(object) -- append object to end'''
        previous_object = self.copy()
        super(NestedList, self).append(self.__convert_child__(obj))
        modify_info = {
            "type": type(self),
            "mode": "append",
            "item": obj,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def extend(self, iterable):
        '''L.extend(iterable) -- extend list by appending elements from the iterable'''
        previous_object = self.copy()
        for item in iterable:
            self.append(self.__convert_child__(item))
        modify_info = {
            "type": type(self),
            "mode": "extend",
            "iterable": iterable,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def insert(self, index, item):
        '''L.insert(index, object) -- insert object before index'''
        previous_object = self.copy()
        super(NestedList, self).insert(index, self.__convert_child__(item))
        modify_info = {
            "type": type(self),
            "mode": "insert",
            "index": index,
            "item": item,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def pop(self, index=-1):
        '''L.pop([index]) -> item -- remove and return item at index (default last).
        Raises IndexError if list is empty or index is out of range.'''
        previous_object = self.copy()
        r = super(NestedList, self).pop(index)
        modify_info = {
            "type": type(self),
            "mode": "pop",
            "index": index,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        return r
        
    def remove(self, value):
        '''L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present.'''
        previous_object = self.copy()
        super(NestedList, self).remove(value)
        modify_info = {
            "type": type(self),
            "mode": "remove",
            "value": value,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def clear(self):
        previous_object = self.copy()
        super(NestedList, self).clear()
        modify_info = {
            "type": type(self),
            "mode": "clear",
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def reverse(self):
        '''L.reverse() -- reverse *IN PLACE*'''
        previous_object = self.copy()
        super(NestedList, self).reverse()
        modify_info = {
            "type": type(self),
            "mode": "reverse",
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])
        
    def sort(self, key=None, reverse=False):
        '''L.sort(cmp=None, key=None, reverse=False) -- stable sort *IN PLACE*;
        cmp(x, y) -> -1, 0, 1'''
        previous_object = self.copy()
        super(NestedList, self).sort(key=key, reverse=reverse)
        modify_info = {
            "type": type(self),
            "mode": "sort",
            "key": key,
            "reverse": reverse,
            "modified_object": self,
            "previous_object": previous_object
        }
        self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self])

# -------------------------------------------------------------------------------------------------------- Dicta Class
class Dicta(dict, ChildConverter, DictUpdater):
    '''
    A dict subclass that observes a nested dict and listens for changes in its data 
    structure. If a data change is registered, Dicta reacts with a callback 
    or a data-export to a JSON file.

    Automatically write data to a JSON file, when the nested data structure changes (optional)
    Throw a callback method, when the nested data structure changes (optional)

    Behaves like a regular dict and supports all dict and list methods like pop(), append(), slice()...
    Supports nesting of all possible datatypes like dict, list, tuple, set and other objects like custom classes.
    Writing data to a file will encode a non-serializable object to a binary-string.
    Reading data from a file will decode a binary-string back to a non-serializable object.
    You can import additional data from json files.
    You can export data to json files.
    
    How to use:
    data = Dicta()
    data = Dicta(dict)
    '''
    
    # --------------------------------- Private Methods
    def __init__(self, *args, **kwargs):
        self.path = None
        self.__prev_data_string = None
        self.callback = None
        self.get_event = False
        self.binary_serializer = False
        self.serializer_hook = default_serializer_hook
        self.update(*args, **kwargs)

    def __call_from_child__(self, modified_object, modify_info, modify_trace):
        self.__current_data_string = self.stringify()
        if self.__current_data_string != self.__prev_data_string:
            if hasattr(self, 'path') and self.path:
                self.__export_file(self.path)
            if hasattr(self, 'callback') and self.callback:
                modify_trace.insert(0, self)
                if self.get_event:
                    self.callback(modify_info)
                else:
                    self.callback()
            self.__prev_data_string = self.__current_data_string

    def __setitem__(self, key, val):
        previous_object = self.copy()
        super(Dicta, self).__setitem__(key, self.__convert_child__(val))
        if hasattr(self, 'callback') and self.callback:
            if self.get_event:
                modify_info = {
                    "type": type(self),
                    "mode": "setitem",
                    "key": key,
                    "value": val,
                    "modified_object": self,
                    "previous_object": previous_object
                }
                self.callback(modify_info)
            else:
                self.callback()
        if hasattr(self, 'path') and self.path and isinstance(self.path, str):
            self.__export_file(self.path)

    def __delitem__(self, key):
        previous_object = self.copy()
        super(Dicta, self).__delitem__(key)
        if self.get_event:
            modify_info = {
                "type": type(self),
                "mode": "delitem",
                "key": key,
                "modified_object": self,
                "previous_object": previous_object
            }
            self.callback(modify_info)
        else:
            self.callback()

    def __rewrite_recursively__(self, obj=None, new=None, init=False):
        if init:
            obj=self
        if not new:
            new={}
        if isinstance(obj, dict):
            new = dict()
            for key, value in obj.items():
                new[key] = self.__rewrite_recursively__(value, new)
        elif isinstance(obj, list):
            new = list()
            for i in range(len(obj)):
                new.append(self.__rewrite_recursively__(obj[i], new))
        elif isinstance(obj, tuple):
            l = []
            for i in range(len(obj)):
                l.append(self.__rewrite_recursively__(obj[i], new))
            new = tuple(l)
        elif isinstance(obj, set):
            new = set(obj)
        else:
            new = obj
        return new
    
    def __serialize__(self):
        if self.binary_serializer:
            dict_str = Serializer(self.serializer_hook).encode(self.dictify())
        else:
            dict_str = json.dumps(self.dictify())
        return dict_str

    def __deserialize__(self, obj):
        if isinstance(obj, dict):
            for key, val in obj.items():
                if isinstance(val, dict) or isinstance(val, list) or isinstance(val, tuple):
                    obj[key] = self.__deserialize__(val)
                if isinstance(val, dict) and self.serializer_hook in val:
                    obj[key] = pickle.loads(val[self.serializer_hook].encode('latin-1'))
        if isinstance(obj, list) or isinstance(obj, tuple):
            for i in range(len(obj)):
                if isinstance(obj[i], dict) or isinstance(obj[i], list) or isinstance(obj[i], tuple):
                    obj[i] = self.__deserialize__(obj[i])
        return obj

    def __import_file(self, path):
        if os.path.exists(path):
            with open(path) as f:
                if self.binary_serializer:
                    data = json.load(f, object_hook=self.__deserialize__)
                else:
                    data = json.load(f)
                f.close()
            self.update(**data)
        else:
            print("Dicta.importFile(): File '{}' does not exist.".format(path))
    
    def __export_file(self, path, reset=True):
        if reset:
            self.__clear_file(path)
        dict_str = self.__serialize__()
        with open(path, 'w') as f:
            f.write(dict_str)
            f.close()
    
    def __clear_file(self, path):
        '''Clear a file. Use with care'''
        with open(path, 'w') as f:
            f.write("{}")
            f.close()
    
    def __remove_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        else:
            print("Dicta.removeFile(): File '{}' does not exist.".format(path))
    
    def __deprecated(self, old_func, new_func=None):
        if new_func:
            print("Attention! The method '{}' is deprecated and will be removed in future updates. Please use '{}' instead.".format(old_func, new_func))
        else:
            print("Attention! The method '{}' is deprecated and will be removed in future updates.".format(old_func))

    # --------------------------------- Public Methods
    # Default dict methods
    def clear(self):
        previous_object = self.copy()
        super(Dicta, self).clear()
        if self.get_event:
            modify_info = {
                "type": type(self),
                "mode": "clear",
                "modified_object": self,
                "previous_object": previous_object
            }
            self.callback(modify_info)
        else:
            self.callback()

    def pop(self, key):
        previous_object = self.copy()
        r = super(Dicta, self).pop(key)
        if self.get_event:
            modify_info = {
                "type": type(self),
                "mode": "pop",
                "key": key,
                "modified_object": self,
                "previous_object": previous_object
            }
            self.callback(modify_info)
        else:
            self.callback()
        return r

    def popitem(self, key):
        previous_object = self.copy()
        r = super(Dicta, self).popitem(key)
        if self.get_event:
            modify_info = {
                "type": type(self),
                "mode": "popitem",
                "key": key,
                "modified_object": self,
                "previous_object": previous_object
            }
            self.callback(modify_info)
        else:
            self.callback()
        return r
    
    def setdefault(self, key, default=None):
        previous_object = self.copy()
        r = super(Dicta, self).setdefault(key, default=default)
        if self.get_event:
            modify_info = {
                "type": type(self),
                "mode": "setdefault",
                "key": key,
                "default": default,
                "modified_object": self,
                "previous_object": previous_object
            }
            self.callback(modify_info)
        else:
            self.callback()
        return r

    def update(self, *args, **kwargs):
        '''Update the data tree with *args and **kwargs
        
        importData(dict)
        importData(key=value,key2=value…)
        
        '''
        DictUpdater.update(self, *args, **kwargs)

    # Custom dict methods
    def bind_callback(self, callback):
        '''Set the callback function'''
        self.callback = callback
        if len(inspect.signature(callback).parameters) > 0:
            self.get_event = True

    def bind_file(self, path, reset=False):
        '''Set the sync file path. Set reset=True if you want to reset the data in the file on startup. Default is False'''
        self.path = path
        if reset or not os.path.exists(path):
            self.__clear_file(path)
        with open(path) as f:
            if self.binary_serializer:
                try:
                    data = json.load(f, object_hook=self.__deserialize__)
                except:
                    print("ERROR!: Dicta.bind_file(): Could not set sync file. File '{}' contains no JSON object. Call Dicta.bind_file(path, reset=True) to overwrite file the content or provide a path to another json file.".format(path))
                    data = {}
                    self.path = None
            else:
                data = json.load(f)
            f.close()
        self.update(**data)
        return data
    
    def pull(self, path=None):
        '''
        Pull/Import data from a JSON file into Dicta.
        
        Dicta.pull() >> pulls data from the file that was binded with Dicta.bind_file(path)
        Dicta.pull('my/path.json') >> pulls data from the file at the given path
        '''
        if path:
            self.__import_file(path)
        elif self.path:
            self.__import_file(self.path)
        else:
            print("Dicta.pull(): Please provide path or bind a sync file first. Use Dicta.bind_file(path)")
    
    def push(self, path, reset=True):
        '''
        Push/Export data to a file. Set reset=True if you want to reset the data in the file at first. Default is True
        '''
        self.__export_file(path, reset)
    
    def clear_file(self, path=None):
        '''
        Clear the file. Use with care.
        
        Dicta.clear_file('my/path.json') >> clears the file at the given path
        Dicta.clear_file() >> clears the file that was binded with Dicta.bind_file(path)
        '''
        if path:
            self.__clear_file(path)
        elif self.path:
            self.__clear_file(self.path)
        else:
            print("Dicta.clearFile(): Please provide path or bind a sync file first. Use Dicta.bind_file(path)")

    def remove_file(self, path=None):
        '''
        Delete a file. Use with care
        
        Dicta.remove_file('my/path.json') >> deletes the file at the given path
        Dicta.remove_file() >> deletes the file that was binded with Dicta.bind_file(path)
        '''
        if path:
            self.__remove_file(path)
        elif self.path:
            self.__remove_file(self.path)
        else:
            print("Dicta.remove_file(): Please provide path or bind a sync file first. Use Dicta.bind_file(path)")

    # Convert all <NestedSet Classes> to <set classes> before serializing,
    # in order to subclass them correctly with <ParentCaller> while loading them
    # back into Dicta while deserializing.
    def dictify(self):
        '''Returns a plain dict representation of the data without Dicta functionality'''
        return self.__rewrite_recursively__(init=True)

    def stringify(self, return_binaries=False):
        '''Returns a string representation of the data in Dicta. Use return_binaries=True, if you want to return binary data also. Default is False'''
        dict_str = self.__serialize__()
        if not return_binaries and self.serializer_hook in dict_str:
            hook_positions = [m.start() for m in re.finditer(self.serializer_hook, dict_str)]
            open_bracket_positions = [m.start() for m in re.finditer("{", dict_str)]
            closed_bracket_positions = [m.start() for m in re.finditer("}", dict_str)]
            closed_bracket_positions.reverse()
            for hook_position in hook_positions:
                hook_begin = None
                for open_bracket in open_bracket_positions:
                    if open_bracket < hook_position:
                        hook_begin = open_bracket
                hook_end = None
                for closed_bracket in closed_bracket_positions:
                    if closed_bracket > hook_position:
                        hook_end = closed_bracket
            dict_str = dict_str.replace(dict_str[hook_begin:hook_end], self.serializer_hook)
        return dict_str

    def set_serializer(self, mode=False, serializer_hook=None):
        '''For security reasons binary serialization of non-serializable objects is 
        deactivated by default. You can activate or deactivate binary serialization 
        with this method (default=False).

        If you activate the binary-serializer all non-serializable objects will be 
        encoded to a binary string and packed into a dict labeled with the key 
        '<serialized-object>'. In case you need this key for your data structure, 
        define a custom serializer-hook by using the serializer_hook parameter (optional). 
        If you don´t use the serializer_hook parameter the default hook '<serialized-object>'
        will be used.
        '''

        if mode:
            self.binary_serializer = True
        else:
            self.binary_serializer = False
        if serializer_hook:
            self.serializer_hook = serializer_hook
        else:
            self.serializer_hook = default_serializer_hook
    
    # Deprecated Methods
    def import_data(self, *args, **kwargs):
        '''
        Deprecated method. Use update() instead.
        Insert/Import data.
        
        importData(dict)
        importData(key=value,key2=value…)
        
        '''
        self.__deprecated("import_data()", "update()")
        self.update(*args, **kwargs)
    
    def import_file(self, path):
        '''
        Deprecated method. Use pull() instead.
        Insert/Import data from a file.
        '''
        self.__deprecated("import_file()", "pull()")
        self.pull(path)
    
    def sync_file(self):
        '''
        Deprecated method. Use pull() instead.
        Pull syncfile data into Dicta.
        
        '''
        self.__deprecated("sync_file()", "pull()")
        self.pull()

    def export_data(self, path, reset=True):
        '''
        Deprecated method! Use push() instead.
        Export data to a file. Set reset=True if you want to reset the data in the file at first. Default is True
        '''
        self.__deprecated("export_data()", "push()")
        self.__export_file(path, reset)

# -------------------------------------------------------------------------------------------------------- Main
if __name__ == "__main__":
    # Declare the 'Dicta' class. Pass a 'path' string and 'callback' method as arguments
    dicta = Dicta()

    # Set Callback method with optional event argument
    def callback(evt):
        print(evt)
    dicta.bind_callback(callback)
    dicta.set_serializer(True)
    dicta.bind_file("data.json", True)
    
    dicta["set"] = {1,2,4,5}
    dicta["set"].add(6)
    dicta["list"] = [1,2,4,5]
    dicta["list"].append(6)


