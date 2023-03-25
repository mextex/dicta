#!/usr/bin/env python

import os
import re
import pickle
import json
import dicta_submodules as ds


default_serializer_hook = "<serialized_object>"


# -------------------------------------------------------------------------------------------------------- Dicta Class
class Dicta(dict, ds.ChildConverter, ds.DictUpdater):
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
    data = Dicta(path="my_data_file.json", callback=my_callback)
    '''
        
    def __init__(self, *args, **kwargs):
        self.path = None
        self.prev_data_string = None
        self.callback = None
        self.callback_args = None
        self.callback_kwargs = None
        self.binary_serializer = False
        self.serializer_hook = default_serializer_hook
        self.update(*args, **kwargs)

    def __call_from_child__(self, modified_object, modify_info, modify_trace):
        self.current_data_string = self.stringify()
        if self.current_data_string != self.prev_data_string:
            if hasattr(self, 'path') and self.path:
                self.exportFile(self.path)
            if hasattr(self, 'callback') and self.callback:
                modify_trace.insert(0, self)
                if self.response:
                    self.callback(modified_object=modified_object, modify_info=modify_info, modify_trace=[self], *self.callback_args, **self.callback_kwargs)    
                else:
                    self.callback(*self.callback_args, **self.callback_kwargs)
            self.prev_data_string = self.current_data_string

    def __setitem__(self, key, val):
        super(Dicta, self).__setitem__(key, self.__convert_child__(val))
        if hasattr(self, 'callback') and self.callback:
            if self.response:
                modify_info = {
                    "type": type(self),
                    "mode": "setitem",
                    "key": key,
                    "value": val
                }
                self.callback(modified_object=self, modify_info=modify_info, modify_trace=[self], *self.callback_args, **self.callback_kwargs)
            else:
                self.callback(*self.callback_args, **self.callback_kwargs)
        if hasattr(self, 'path') and self.path and isinstance(self.path, str):
            self.exportFile(self.path)

    def __delitem__(self, key):
        super(Dicta, self).__delitem__(key)
        if self.response:
            modify_info = {
                "type": type(self),
                "mode": "delitem",
                "key": key
            }
            self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self], *self.callback_args, **self.callback_kwargs)
        else:
            self.callback(*self.callback_args, **self.callback_kwargs)

    def clear(self):
        super(Dicta, self).clear()
        if self.response:
            modify_info = {
                "type": type(self),
                "mode": "clear"
            }
            self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self], *self.callback_args, **self.callback_kwargs)
        else:
            self.callback(*self.callback_args, **self.callback_kwargs)

    def pop(self, key):
        r = super(Dicta, self).pop(key)
        if self.response:
            modify_info = {
                "type": type(self),
                "mode": "pop",
                "key": key
            }
            self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self], *self.callback_args, **self.callback_kwargs)
        else:
            self.callback(*self.callback_args, **self.callback_kwargs)
        return r

    def popitem(self, key):
        r = super(Dicta, self).popitem(key)
        if self.response:
            modify_info = {
                "type": type(self),
                "mode": "popitem",
                "key": key
            }
            self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self], *self.callback_args, **self.callback_kwargs)
        else:
            self.callback(*self.callback_args, **self.callback_kwargs)
        return r
    
    def setdefault(self, key, default=None):
        r = super(Dicta, self).setdefault(key, default=default)
        if self.response:
            modify_info = {
                "type": type(self),
                "mode": "setdefault",
                "key": key,
                "default": default
            }
            self.call_to_parent(modified_object=self, modify_info=modify_info, modify_trace=[self], *self.callback_args, **self.callback_kwargs)
        else:
            self.callback(*self.callback_args, **self.callback_kwargs)
        return r

    def update(self, *args, **kwargs):
        '''Update the data tree with *args and **kwargs'''
        ds.DictUpdater.update(self, *args, **kwargs)

    def bind(self, callback, response=None, *args, **kwargs):
        '''Set the callback function'''
        self.callback = callback
        self.response = response
        self.callback_args = args
        self.callback_kwargs = kwargs
        
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

    def syncFile(self, path, reset=False):
        '''Set the sync file path. Set reset=True if you want to reset the data in the file on startup. Default is False'''
        self.path = path
        if reset or not os.path.exists(path):
            self.clearFile(path)
        with open(path) as f:
                if self.binary_serializer:
                    data = json.load(f, object_hook=self.__deserialize__)
                else:
                    data = json.load(f)
                f.close()
        self.update(**data)
        return data
    
    def importFile(self, path):
        '''Insert/Import data from a file.'''
        if os.path.exists(path):
            with open(path) as f:
                if self.binary_serializer:
                    data = json.load(f, object_hook=self.__deserialize__)
                else:
                    data = json.load(f)
                f.close()
            self.update(**data)
        else:
            print("Dicta -> importFile: File '{}' does not exist.".format(path))
        
    # Convert all <NestedSet Classes> to <set classes> before serializing,
    # in order to subclass them correctly with <ParrentCaller> while loading them
    # back into Dicta while deserializing.
    def dictify(self):
        '''Returns a plain dict representation of the data without Dicta functionality'''
        return self.__rewrite_recursively__()
    
    def __rewrite_recursively__(self, obj=None, new=None):
        if not obj:
            obj=self
        if not new:
            new={}
        if isinstance(obj, dict):
            new = dict()
            for key, value in obj.items():
                if bool(value):
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
            dict_str = ds.Serializer(self.serializer_hook).encode(self.dictify())
        else:
            dict_str = json.dumps(self.dictify())
        return dict_str

    def exportFile(self, path, reset=True):
        '''Export data to a file. Set reset=True if you want to reset the data in the file at first. Default is True'''
        if reset:
            self.clearFile(path)
        dict_str = self.__serialize__()
        with open(path, 'w') as f:
            f.write(dict_str)
            f.close()
    
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
    
    def clearFile(self, path):
        '''Clear a file. Use with care'''
        with open(path, 'w') as f:
                f.write("{}")
                f.close()

    def removeFile(self, path):
        '''Delete a file. Use with care'''
        if os.path.exists(path):
            os.remove(path)
        else:
            print("Dicta -> removeFile: File '{}' does not exist.".format(path))
    
    def setBinarySerializer(self, mode=False, serializer_hook=None):
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
            


# -------------------------------------------------------------------------------------------------------- Main
if __name__ == "__main__":
    # Declare the 'Dicta' class. Pass a 'path' string and 'callback' method as arguments
    dicta = Dicta()

    # Set Callback method with optional *args and *kwargs
    # add a **kwargs parameter to the callback function if you want response (default is False). 
    # Default Resonse: modified_object(class), modify_info(dict), modify_trace(list)
    def callback(response_string):
        print(dicta)
    dicta.bind(callback, response_string="Data changed to: ", response=False)
    dicta.setBinarySerializer(True)
    dicta.syncFile("data.json", True)
    
    dicta["set"] = {1,2,4,5}
    dicta["set"].add(6)
    dicta["list"] = [1,2,4,5]
    dicta["list"].append(6)
    
