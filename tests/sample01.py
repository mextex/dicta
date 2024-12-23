import dicta

data = {}
data["str_key"] = "hello"

d = dicta.Dicta(data)
d.bind_file("data.json")
d["int_key"] = 9

d.update(float_key=3.14,another_str_key="world!")

print(d.stringify())