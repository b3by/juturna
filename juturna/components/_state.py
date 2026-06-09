from collections import UserDict


class State(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ops = dict()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        self._ops[key] = ('SET', value)

    def __delitem__(self, key):
        _deleted = super().__delitem__(key)

        self._ops[key] = ('DEL', None)

        return _deleted

    def deltas(self):
        _ops = [
            (action, key, value) for key, (action, value) in self._ops.items()
        ]

        self._ops.clear()

        return _ops

    def apply(self, deltas):
        for _op, key, value in deltas:
            if _op == 'SET':
                super().__setitem__(key, value)
            elif _op == 'DEL':
                super().__delitem__(key)
