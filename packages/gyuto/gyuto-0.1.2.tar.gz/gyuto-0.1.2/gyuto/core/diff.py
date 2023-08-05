from gyuto.core import *


class Diff(object):
    """Diff of two python dictionaries"""

    def __init__(self, l_dict, r_dict):
        self.l_dict, self.r_dict = l_dict, r_dict
        self.l_keys, self.r_keys = set(l_dict.keys()), set(r_dict.keys())
        self.i_keys = self.l_keys.intersection(self.r_keys)

    def l_keys_uniq(self):
        return self.l_keys - self.i_keys

    def r_keys_uniq(self):
        return self.r_keys - self.i_keys

    def keys_same(self):
        return [k for k in self.i_keys if self.l_dict[k] == self.r_dict[k]]

    def keys_diff(self):
        return [k for k in self.i_keys if self.l_dict[k] != self.r_dict[k]]
