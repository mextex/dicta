# dicta

A dict subclass that observes a nested dict and listens for changes in its data structure. If a data change is registered, Dicta reacts with a callback or a data-export to a JSON file.

## Core Functionality

- Throw a callback, when the nested data structure changes
- Write data to a JSON file, when the nested data structure changes

## Features

- Behaves like a regular `dict` and supports all `dict`, `list`, `tuple` and `set` methods.
- Supports nesting of all possible datatypes like `dict`, `list`, `tuple`, `set` and other objects like custom classes.
- Encodes non-serializable objects to a binary-string when writing data to a file (Optional / deactivated by default).
- Reading data from a file will decode a binary-string back to a non-serializable object (Optional / deactivated by default).
- Import/Insert additional data from json files.
- Export data to json files.


## Install

```
pip3 install dicta
```

## How to use

```python
# Declare the 'Dicta' class.
dicta = Dicta()

# Activate binary serialization
dicta.setBinarySerializer(True)

# Set a synch file path.
dicta.synchFile("data.json")

# Define the callback method
def callback():
    print("Data changed!")
    print(dicta)

# Bind the callback method to dicta
dicta.bind(callback)

# Add data
dicta["entities"] = {}
dicta["entities"]["persons"] = []

dicta["entities"]["persons"].append({"name":"john", "age":23})
dicta["entities"]["persons"].append({"name":"peter", "age":13})

# Update a key in a dict
dicta["entities"]["persons"][1]["age"] = 42

# Add another nested list to the dict
dicta["entities"]["animals"] = []
dicta["entities"]["animals"].append("lion")
dicta["entities"]["animals"].append("elephant")

# Slice item from list
del dicta["entities"]["animals"][0:1]

# Remove item from dict
dicta["entities"].pop("persons")

# and so forth…
# Should support all regular dict behaviours and 
# list methods (pop(), append(), slice(), insert() …)

# Import additional data from another file. 
# (New data will be added. Old data remains but will 
# be overwritten if dict keys match.)
dicta.insert("additional_data_file.json")

# Export the data to another file
dicta.export("data_backup.json")

# Get string representation of the Dicta
dicta.stringify()
```

## Reference

---

#### Dicta()

```python
Dicta(*args, **kwargs)
```

A dict subclass.

###### **Parameter**

- ***args** *(Optional)*
- ****kwargs** *(Optional)*

###### **Return**

- **Dicta Class**

---

### Methods

#### Dicta Methods

---

##### Dicta.bind()

```python
Dicta.bind(callback, response=False, *args, *kwargs)
```

Sets the callback method for the Dicta Class. If `response=False` (default) the callback method only gets the `*args, *kwargs` as parameters you define. If `response=True` the callback method gets response from the Dicta Class. You should define your callback function with a `*kwargs` parameter or with three positional parameters:

`def my_callback(**kwargs)`

or

`def my_callback(modifed_object, modify_info, modify_trace)`

###### **Parameter**

- **callback** *(method)*
- **default_response** *(bool) (optional / default = False)*

###### **Callback**

- **args** as defined in setCallback *(optional / default: None)*
- **kwargs** as defined in setCallback *(optional / default: None)*
- **modifed_object** *(object)*
- ***modify_info*** *(json_string)*: Contains info about the data mod
- **modify_trace** *(list)*: Contains the dict-tree-path to the modified object as a list starting from root*

---

##### Dicta.syncFile()

```python
Dicta.syncFile(path, reset=False)
```

Sets the sync file to automatically store the data on data change. If `reset=False` (default) old data will remain and will be updated with new data . If `reset=True` the data wil be cleared when `syncFile()` is called.

**This will fail if your dict contains non-serializable objects and binary serialization is not activated.** For security reasons this is deactivated by default. You can activate binary serialization manually with `Dicta.useBinarySerializer(True)`.

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a `dict` labeled with the key `'<serialized-object>'`. See the reference for `Dicta.useBinarySerializer()`.

###### **Parameter**

- **path** *(string)*
- **reset** *(bool) (optional / default = False)*

---

##### Dicta.importFile()

```python
Dicta.importFile(path)
```

Import data from a file. New data will be added to the DictObsercer, old data remains but will be overwritten if dict keys match.

###### **Parameter**

- **path** *(string)*

---

##### Dicta.exportFile()

```python
Dicta.exportFile(path, reset=True)
```

Export data to a file. If `reset=True` the data wil be cleared when `exportFile()` (default) is called . If `reset=False` the data will be updated.

**This will fail if your dict contains non-serializable objects and binary serialization is not activated.** For security reasons this is deactivated by default. You can activate binary serialization by calling `Dicta.useBinarySerializer(True)` before.

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a `dict` labeled with the key `'<serialized-object>'`. See the reference for `Dicta.useBinarySerializer()`.

###### **Parameter**

- **path** (string)
- **reset** *(bool) (optional / default = True)*

---

##### Dicta.clearFile()

```python
Dicta.clearFile(path)
```

Clear a file.

###### **Parameter**

- **path** *(string)*

---

##### Dicta.removeFile()

```python
Dicta.removeFile(path)
```

Remove a data file.

###### **Parameter**

- **path** *(string)*

---

##### Dicta.dictify()

```python
Dicta.dictify()
```

Returns a plain dict representation of the data without Dicta functionality.

###### **Parameter**

- None

###### **Return**

- **dict**

---

##### Dicta.stringify()

```python
Dicta.stringify(returnBinaries=False)
```

Returns a string representation of the data in Dicta.

**This will fail if your dict contains non-serializable objects and binary serialization is not activated.** For security reasons this is deactivated by default. You can activate binary serialization by calling `Dicta.useBinarySerializer(True)` before.

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a `dict` labeled with the key `'<serialized-object>'`. See the reference for `Dicta.useBinarySerializer()`.

For better readability serialized objects won´t be returned by default and are replaced by a the `'<serialized-object>'` hook. If you want to return the binaries set the `return_binaries`parameter to `True`.

###### **Parameter**

- **return_binaries** *(bool) (default = False)*

###### **Return**

- **string**

---

##### Dicta.setBinarySerializer()

```python
Dicta.setBinarySerializer(binary_serializer=False, serializer_hook='<serialized-object>')
```

For security reasons binary serialization of non-serializable objects is deactivated by default. You can activate or deactivate binary serialization with this method (default=False).

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a dict labeled with the key `'<serialized-object>'`. In case you need this key for your data structure, define a custom serializer-hook by using the `serializer_hook` parameter (optional). If you don´t use the `serializer_hook` parameter the default hook `'<serialized-object>'` will be used.

###### Parameter

- **use_binary_serializer** *(bool) (default = False)*
- **serializer_hook** *(string) (optional / default = '\<serialized-object>')*

###### Example

```python
myDictObserver.useBinarySerializer(True, '<my_serialzer_hook>')
```

---

#### Data Type Methods

Behaves like a regular nested dict and supports all data type methods. Adding, removing, modifiying and accessing of nested elements should work out of the box. For example:

---

##### NestedDict.update()

```python
NestedDict.update(*args, *kwargs)
```

---

##### NestedDict.clear()

```python
NestedDict.clear()
```

---

##### NestedDict.pop()

```python
NestedDict.pop(key)
```

---

##### NestedDict.popitem()

```python
NestedDict.popitem(key)
```

---

##### NestedDict.setdefault()

```python
NestedDict.setdefault(key, default=None)
```

*and so forth: keys(), iter() …*

---

##### NestedList.append()

```python
NestedList.append(item)
```

*and so forth: pop()…*

---

## Dependencies

- os
- re
- json
- pickle
