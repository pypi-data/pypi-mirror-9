import json


class Database(object):
    """
    This is a class that manages a file database which
    stores information in json format.
    """

    def __init__(self, file_path):
        """
        Constructor takes the file path of the database as a parameter.
        """
        from os import path, stat

        # Create the file if it does not exist or is empty
        if not path.exists(file_path) or stat(file_path).st_size == 0:
            new_file = open(file_path, "w+")
            json.dump({}, new_file)
            new_file.close()

        self.path = file_path

    def set_path(self, file_path):
        from os import path, stat

        # Create the file if it does not exist or is empty
        if not path.exists(file_path) or stat(file_path).st_size == 0:

            # Copy the content from the previous database to the new database
            with open(self.path) as f:
                with open(file_path, "w+") as f1:
                    for line in f:
                        f1.write(line)

        self.path = file_path

    def _get_content(self, key=None):
        db = open(self.path, "r+")
        content = db.read()
        obj = json.loads(content)
        db.close()

        if key:
            if key in obj.keys():
                return obj[key]
            else:
                return None

        return obj

    def _set_content(self, key, value):
        obj = self._get_content()
        obj[key] = value

        with open(self.path, "w+") as db:
            json.dump(obj, db)

    def delete(self, key):
        """
        Takes a key and removes the entry from the database.
        """
        obj = self._get_content()
        obj.pop(key, None)

        with open(self.path, "w+") as db:
            json.dump(obj, db)

    def data(self, **kwargs):
        """
        If a key is passed in, a corresponding value will be returned.
        If a key-value pair is passed in then the corresponding key in
        the database will be set to the specified value.
        A dictionary can be passed in as well.
        If a key does not exist and a value is provided then an entry
        will be created in the database.
        """

        key = kwargs.pop('key', None)
        value = kwargs.pop('value', None)
        dictionary = kwargs.pop('dictionary', None)

        # Fail if a key and a dictionary or a value and a dictionary are given
        if (key is not None and dictionary is not None) or \
           (value is not None and dictionary is not None):
            raise ValueError

        # If only a key was provided return the corresponding value
        if key is not None and value is None:
            return self._get_content(key)

        # if a key and a value are passed in
        if key is not None and value is not None:
            self._set_content(key, value)

        if dictionary is not None:
            for key in dictionary.keys():
                value = dictionary[key]
                self._set_content(key, value)

        return self._get_content()

    # Iterator methods

    def __len__(self):
        return len(self._get_content())

    def __iter__(self):
        return iter(self._get_content().keys())

    def __list__(self):
        return list(self._get_content().keys())

    # Dictionary compatibility methods

    def __getitem__(self, key):
        return self.data(key=key)

    def __setitem__(self, key, value):
        return self.data(key=key, value=value)

    def __delitem__(self, key):
        return self.delete(key=key)

    def __contains__(self, key):
        return key in self._get_content()
