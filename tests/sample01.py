import dicta

data = {}
data["str_key"] = "hello"

d = dicta.Dicta(data)
d.bind_file("data.json")
d["int_key"] = 0
d.update(float_key=3.14,another_str_key="world!")
d["dict_key"] = {"key1": "value1", "key2": "value2"}

def callback():
    print("bool_key changed to", d["bool_key"])

d.bind_callback(callback)

d["bool_key"] = False
d["bool_key"] = True

print(d.stringify())