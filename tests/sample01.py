import dicta

data = {}
data["str_key"] = "hello"

d = dicta.Dicta(data)
d.syncFile("data.json")
d["int_key"] = 9

d.importData(float_key=3.14,another_str_key="world!")

print(d.stringify())