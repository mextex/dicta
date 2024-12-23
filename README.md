# dicta

Dicta is a dict subclass that behaves like a normal nested dict but adds some key functions:

- dicta detects data changes and throws a callback if that is the case (optional).

- dicta automatically syncs its data with a JSON file (optional).

- dicta imports & exports data from JSON files

## Features

- Behaves like a regular `dict` and supports all `dict`, `list`, `tuple` and `set` methods.
- Supports nesting of all possible datatypes like `dict`, `list`, `tuple`, `set` and other objects like custom classes.
- Encodes non-serializable objects to a binary-string when writing data to a file (Optional / deactivated by default).
- Reading data from a file will decode a binary-string back to a non-serializable object (Optional / deactivated by default).
- Import/Insert additional data from json files.
- Export data to json files.

## Install

```bash
pip3 install dicta
```

## How to use

```python
import dicta

# ------------ Core functionality:

# Declare the 'Dicta' class.
dicta = dicta.Dicta()

# Set a sync file path.
dicta.bind_file("data.json")

# Define a callback method
def callback():
    print("Data changed!")
    print(dicta)

# Bind the callback method to dicta
dicta.bind_callback(callback)

# Add data in the same way as if you would use a normal dict:
dicta.update({"key":"value"})
dicta.update(key2=value2, key3=value3)
dicta["entities"] = {}
dicta["entities"]["persons"] = []
dicta["entities"]["persons"].append({"name":"john", "age":23})
dicta["entities"]["persons"].append({"name":"peter", "age":24})

# Use regular dict methods
del dicta["entities"]["persons"][0:1]
dicta["entities"].pop("persons")


# ------------ Other dicta methods:

# Import data from file:
dicta.import_file("additional_data_file.json")

# Export the data to file
dicta.export_file("data_backup.json")

# Get string representation of the Dicta
string_representation = dicta.stringify()

# Get dict representation of the Dicta
dict_representation = dicta.dictify()

# Activate binary serialization, if you want to store custom data objects in a sync file:
dicta.set_serializer(True)
```

## Reference

### Dicta()

```python
Dicta(*args, **kwargs)
Dicta(dict)
Dicta(key=value,key2=value)
```

A dict subclass.

#### **Parameter**

- ***args** *(Optional)*
- ****kwargs** *(Optional)*

#### **Return**

- **Dicta Class**

---

### Methods

#### Dicta Methods

##### Dicta.bind_callback()

```python
Dicta.bind_callback(callback, response=False, *args, *kwargs)
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

##### Dicta.bind_file()

```python
Dicta.bind_file(path, reset=False)
```

Sets the sync file to automatically store the data on data change. If `reset=False` (default) old data will remain and will be updated with new data . If `reset=True` the data wil be cleared when `syncFile()` is called.

**Data sync is monodirectional!** Though the data is automatically synced to your syncfile data is not synced to your dicta instance if filedata changes. Use Dicta.sync_file() to pull data from file into your dict.

**Sync will fail if your dict contains non-serializable objects and binary serialization is not activated.** For security reasons this is deactivated by default. You can activate binary serialization manually with `Dicta.set_serializer(True)`.

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a `dict` labeled with the key `'<serialized-object>'`. See the reference for `Dicta.set_serializer()`.

###### **Parameter**

- **path** *(string)*
- **reset** *(bool) (optional / default = False)*

---

##### Dicta.sync_file()

```python
Dicta.sync_file()
```

Pulls data from the binded sync file into your Dicta instance.

---

##### Dicta.import_file()

```python
Dicta.import_file(path)
```

Import data from a file. New data will be added to the DictObsercer, old data remains but will be overwritten if dict keys match.

###### **Parameter**

- **path** *(string)*

---

##### Dicta.export_file()

```python
Dicta.export_file(path, reset=True)
```

Export data to a file. If `reset=True` the data wil be cleared when `export_file()` (default) is called . If `reset=False` the data will be updated.

**This will fail if your dict contains non-serializable objects and binary serialization is not activated.** For security reasons this is deactivated by default. You can activate binary serialization by calling `Dicta.set_serializer(True)` before.

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a `dict` labeled with the key `'<serialized-object>'`. See the reference for `Dicta.set_serializer()`.

###### **Parameter**

- **path** (string)
- **reset** *(bool) (optional / default = True)*

---

##### Dicta.clear_file()

```python
Dicta.clear_file(path)
```

Clear a file.

###### **Parameter**

- **path** *(string)*

---

##### Dicta.remove_file()

```python
Dicta.remove_file(path)
```

Remove a data file.

###### **Parameter**

- **path** *(string)*

---

##### Dicta.import_data(*args,**kwargs)

```python
Dicta.import_data(dict)
Dicta.import_data(key=value,key2=value2…)
```

Import data as dict or key/value pairs. Same as Dica.update(*args,**kwargs)

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

**This will fail if your dict contains non-serializable objects and binary serialization is not activated.** For security reasons this is deactivated by default. You can activate binary serialization by calling `Dicta.set_serializer(True)` before.

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a `dict` labeled with the key `'<serialized-object>'`. See the reference for `Dicta.set_serializer()`.

For better readability serialized objects won´t be returned by default and are replaced by a the `'<serialized-object>'` hook. If you want to return the binaries set the `return_binaries`parameter to `True`.

###### **Parameter**

- **return_binaries** *(bool) (default = False)*

###### **Return**

- **string**

---

##### Dicta.set_serializer()

```python
Dicta.set_serializer(binary_serializer=False, serializer_hook='<serialized-object>')
```

For security reasons binary serialization of non-serializable objects is deactivated by default. You can activate or deactivate binary serialization with this method (default=False).

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a dict labeled with the key `'<serialized-object>'`. In case you need this key for your data structure, define a custom serializer-hook by using the `serializer_hook` parameter (optional). If you don´t use the `serializer_hook` parameter the default hook `'<serialized-object>'` will be used.

###### Parameter

- **binary_serializer** *(bool) (default = False)*
- **serializer_hook** *(string) (optional / default = '\<serialized-object>')*

###### Example

```python
myDicta.set_serializer(True)
myDicta.set_serializer(True, '<my_serialzer_hook>')
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
