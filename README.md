# Dicta

**Dicta** is a subclass of Python's `dict` that behaves like a normal nested dictionary but with added key features:

- Detects changes in its data structure and triggers a callback (optional).
- Automatically syncs its data with a JSON file (optional).
- Imports and exports data from JSON files.

## Features

- Behaves like a regular `dict` and supports all `dict`, `list`, `tuple`, and `set` methods.
- Supports nesting of various data types including `dict`, `list`, `tuple`, `set`, and custom objects.
- Optionally encodes non-serializable objects to a binary string when writing data to a file.
- Decodes binary strings back to non-serializable objects when reading from a file.
- Imports additional data from JSON files.
- Exports data to JSON files.

## Installation

To install Dicta, use pip:

```bash
pip3 install dicta
```

## Usage

Here's how to use Dicta:

```python
import dicta

# Core functionality:

# Declare the 'Dicta' class.
my_dicta = dicta.Dicta()

# Set a sync file path.
my_dicta.bind_file("data.json")

# Define a callback method
def callback():
    print("Data changed!")
    print(my_dicta)

# Bind the callback method to dicta
my_dicta.bind_callback(callback)

# Add data as you would with a normal dict:
my_dicta.update({"key": "value"})
my_dicta.update(key2="value2", key3="value3")
my_dicta["entities"] = {}
my_dicta["entities"]["persons"] = []
my_dicta["entities"]["persons"].append({"name": "john", "age": 23})
my_dicta["entities"]["persons"].append({"name": "peter", "age": 24})

# Use regular dict methods
del my_dicta["entities"]["persons"][0:1]
my_dicta["entities"].pop("persons")

# Dicta methods:

# Import data from a file:
my_dicta.pull("additional_data_file.json")

# Export the data to a file
my_dicta.push("data_backup.json")

# Get string representation of the Dicta
print(my_dicta.stringify())

# Get dict representation of the Dicta
dict_representation = my_dicta.dictify()

# Activate binary serialization to store sets or custom data objects in a sync file
my_dicta.set_serializer(True)
my_dicta["set"] = {1,2,4,5}
my_dicta["set"].add(6)
```

## Reference

### Dicta Class

```python
Dicta(*args, **kwargs)
Dicta(dict)
Dicta(key=value,key2=value)
```

A ```dict``` subclass.

#### **Parameters**

- **args** (Optional)
- **kwargs** (Optional)

#### **Return**

- **Dicta Class**

---

### Methods

#### Dicta Methods

##### Dicta.bind_callback()

```python
Dicta.bind_callback(callback)
```

Sets the callback method for the Dicta Class. Pass an event argument (optional) to receive the data modification event:

```python
def my_callback(): 
    print(dicta)
Dicta.bind_callback(my_callback)
```

or

```python
def my_callback(event): 
    print(event)
Dicta.bind_callback(my_callback)
```

###### **Parameter**

- **callback** *(method)*

###### **Callback**

- **event** *(dict)*


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

##### Dicta.pull()

```python
Dicta.pull(path=None)     
```

Import data from a given JSON file (if *path* argument is given) or the binded sync file (if no *path* argument is given) into your Dicta instance. New data will be added to the DictObsercer, old data remains but will be overwritten if dict keys match.

```python
Dicta.pull() >> pulls data from the file that was binded with Dicta.bind_file(path)
Dicta.pull('my/path.json') >> pulls data from the file at the given path        
```

###### **Parameter**

- **path** *(string) (optional / default = None)*

---

##### Dicta.push()

```python
Dicta.push(path, reset=True)
```

Export/Push data to a file. If `reset=True` the file will be cleared before pushing (default). If `reset=False` the data will be updated.

**This will fail if your dict contains non-serializable objects and binary serialization is not activated.** For security reasons this is deactivated by default. You can activate binary serialization by calling `Dicta.set_serializer(True)` before.

If you activate the binary-serializer all non-serializable objects will be encoded to a binary string and packed into a `dict` labeled with the key `'<serialized-object>'`. See the reference for `Dicta.set_serializer()`.

###### **Parameter**

- **path** (string)
- **reset** *(bool) (optional / default = True)*

---

##### Dicta.clear_file()

```python
Dicta.clear_file(path=None)
```

Clear a file.

```python
Dicta.clear_file() >> Clears the binded sync file.
Dicta.clear_file('my/path.json') >> Clears the file at a given path.
```

###### **Parameter**

- **path** *(string) (optional / default = None)*

---

##### Dicta.remove_file()

```python
Dicta.remove_file(path=None)
```

Remove a data file.

```python
Dicta.remove_file() >> Removes the binded sync file.
Dicta.remove_file('my/path.json') >> Removes the file at a given path.
```

###### **Parameter**

- **path** *(string) (optional / default = None)*

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

and so forth: keys(), iter() …

---

##### NestedList.append()

```python
NestedList.append(item)
```

and so forth: pop()…

---

#### Deprecated Methods

##### Dicta.import_data(*args,**kwargs)

```python
Dicta.import_data(dict)
Dicta.import_data(key=value,key2=value2…)
```

Import data as dict or key/value pairs. Same as Dica.update(*args,**kwargs)

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

## Dependencies

- os
- re
- json
- pickle
