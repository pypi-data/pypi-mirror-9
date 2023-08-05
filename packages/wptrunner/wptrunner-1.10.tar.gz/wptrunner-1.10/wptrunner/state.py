class State(object):
    filename = os.path.join(here, ".wpt-update.lock")

    def __new__(cls):
        rv = cls.load()
        if rv is not None:
            logger.debug("Existing state found")
            return rv

        logger.debug("No existing state found")
        return object.__new__(cls, parent)

    def __init__(self, parent=None):
        """Object containing state variables created when running Steps.

        On write the state is serialized to disk, such that it can be restored in
        the event that the program is interrupted before all steps are complete.
        Note that this only works well if the values are immutable; mutating an
        existing value will not cause the data to be serialized.

        Variables are set and get as attributes e.g. state_obj.spam = "eggs".

        :param parent: Parent State object or None if this is the root object.
        """

        if hasattr(self, "_data"):
            return

        self._parent = parent
        self._data = [{}]

    @classmethod
    def load(cls):
        """Load saved state from a file"""
        try:
            with open(cls.filename) as f:
                try:
                    rv = pickle.load(f)
                    logger.debug("Loading data %r" % (rv._data,))
                    return rv
                except EOFError:
                    logger.warning("Found empty state file")
        except IOError:
            logger.debug("IOError loading stored state")

    def push(self, init_values):
        """Push a new clean state dictionary

        :param init_values: List of variable names in the current state dict to copy
                            into the new state dict."""

        new_state = {}
        for key in init_values:
            setattr(new_state, key, self._data[-1][key])
        self._data.push(new_state)

    def pop(self, name):
        """Remove the current state dictionary"""
        if len(self._data) > 1:
            self._data.pop()
        else:
            raise ValueError("Tried to pop the top state")

    def save(self):
        """Write the state to disk"""
        with open(self.filename, "w") as f:
            pickle.dump(self, f)

    def is_empty(self):
        return len(self._data) == 1 and self._data[1] == {}

    def clear(self):
        """Remove all state and delete the stored copy."""
        try:
            os.unlink(self.filename)
        except OSError:
            pass
        self._data = [{}]


    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self._data[-1][key] = value
            self.save()

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError
        try:
            return self._data[-1][key]
        except KeyError:
            raise AttributeError

    def __contains__(self, key):
        return key in self._data[-1]

    def update(self, items):
        """Add a dictionary of {name: value} pairs to the state"""
        self._data[-1].update(items)
        self.save()

    def keys(self):
        return self._data[-1].keys()
