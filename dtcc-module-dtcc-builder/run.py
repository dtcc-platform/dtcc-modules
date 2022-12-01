import importlib, inspect


for name, cls in inspect.getmembers(importlib.import_module("tools"), inspect.isclass):
    if cls.__module__ == "tools":
        print(name)
        cls(publish=False).listen()