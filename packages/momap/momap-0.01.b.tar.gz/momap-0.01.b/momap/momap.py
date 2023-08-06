import sortedcontainers

class momap(object):
    def __init__(self, *args, **kwargs):
        if len(args) > 0 and len(kwargs) > 0:
            raise Exception("Wrong Initialization")

        self._dict = sortedcontainers.SortedDict()
        if len(kwargs) > 0:
            # A normal map
            for k, v in kwargs.items():
                self._dict[k] = [v]
        elif len(args) > 0:
            for tup in args[0]:
                assert(len(tup) == 2)
                self.add(tup[0], tup[1])

    def __setitem__(self, key, value):
        '''Overwrite previous value
        '''
        self._dict[key] = [value]
    def __getitem__(self, key):
        '''Return the first element of the key
        '''
        return self._dict[key][0]
    def __contains__(self, key):
        return self._dict.__contains__(key)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        repr_dict = ""
        for k, v in self._dict.items():
            repr_dict += str(k) + ": " + repr(v) + ", "
        repr_dict = repr_dict.rstrip(', ')
        return '%s{%s}' % (self.__class__.__name__, repr_dict)

    def add(self, key, value):
        if key in self._dict:
            self._dict[key].append(value)
        else:
            self._dict[key] = [value]

    def get_list(self, key):
        return self._dict[key]

    def items(self):
        return list(self._dict.items())

if __name__ == '__main__':
    print("Hello!")
