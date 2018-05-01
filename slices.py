import collections.abc
import functools
import unittest

def lexical_less(it1, it2):
    sentinel = object()
    for x, y in itertools.zip_longest(it1, it2, fillvalue=sentinel):
        if x is sentinel:
            return True
        elif y is sentinel:
            return False
        elif x < y:
            return True
        elif y < x:
            return False
    return False

@functools.total_ordering
class FrozenSliceView(collections.abc.Sequence):
    def __init__(self, seq, start=None, stop=None, step=None):
        self.seq = seq
        if isinstance(start, range) and stop is None and step is None:
            self.range = start
        else:
            sl = slice(start, stop, step)
            self.range = range(*sl.indices(len(seq)))
    def __len__(self):
        return len(self.range)
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return type(self)(self.seq, self.range[idx])
        else:
            return self.seq[self.range[idx]]
    def __repr__(self):
        return f'{type(self).__name__}({self.seq}, {self.range.start}, {self.range.stop}, {self.range.step})'
    def __str__(self):
        return str(list(self))
    def __eq__(self, other):
        return (isinstance(other, (SliceView, type(self.seq))) and
                all(x==y for x,y in zip(self, other)))
    def __lt__(self, other):
        if not isinstance(other, (SliceView, type(self.seq))):
            raise TypeError(f"'<' not supported between instances of '{type(self)}' and '{type(other)}'")
        return lexical_less(self, other)

@functools.total_ordering
class SliceView(FrozenSliceView, collections.abc.MutableSequence):
    def __setitem__(self, idx, val):
        if isinstance(idx, slice):
            r = self.range[idx]
            if len(r) != len(val):
                raise TypeError(f'{type(self).__name__} cannot insert or delete items')
            self.seq[r.start:r.stop:r.step] = val
        else:
            self.seq[self.range[idx]] = val
    def __delitem__(self, idx):
        raise TypeError(f'{type(self).__name__} cannot delete items')
    def insert(self, idx, value):
        raise TypeError(f'{type(self).__name__} cannot insert items')

class TestSliceView(unittest.TestCase):
    def _test_frozen(self, r, s):
        r2 = range(19, 13, -2)
        if not isinstance(r, range):
            r2 = type(r)(r2)
        self.assertEqual(s[::-2], r2)
        with self.assertRaises(TypeError):
            s[0] = 0
    def _test_mutate(self, r, s):
        s[0] = 0
        s[-2::-2] = 1,2,3
        self.assertEqual(r[:10], [10, 11, 12, 0, 3, 15, 2, 17, 1, 19])
        with self.assertRaises(TypeError):
            del s[0]
        with self.assertRaises(TypeError):
            s += [3]
        with self.assertRaises(TypeError):
            s[-1::-2] = 1,2,3
    def test_frozen(self):
        r = range(10, 30)
        self._test_frozen(r, FrozenSliceView(r, 3, 10))
        self._test_frozen(r, SliceView(r, 3, 10))
        l = list(r)
        self._test_frozen(l, FrozenSliceView(l, 3, 10))
    def test_mutate(self):
        l = list(range(10, 30))
        self._test_mutate(l, SliceView(l, 3, 10))
    
if __name__ == '__main__':
    unittest.main()
