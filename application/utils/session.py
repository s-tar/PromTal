class Session():
    def __init__(self, data):
        self.__dict__.update({'_Session__data': data})

    def __getattr__(self, item):
        if hasattr(self.__data, item):
            return getattr(self.__data, item)

        return self.__data.get(item, None)

    def __setattr__(self, key, value):
        if hasattr(self.__data, key):
            raise KeyError("Key '%s' is reserved" % key)
        else:
            self.__data[key] = value