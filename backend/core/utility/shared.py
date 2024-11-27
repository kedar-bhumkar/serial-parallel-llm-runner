# Singleton instance for passing high compute data between modules. Works as a cache

shared_data_instance = None
class SharedData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedData, cls).__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def get_data(self, key):
        return self.data.get(key, None)

    def set_data(self, key, value):
        self.data[key] = value

shared_data_instance = SharedData()
