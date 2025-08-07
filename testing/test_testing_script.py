from bidsbuilder.util.hooks.containers import *


t = {"a":1,
     "b":2,
     "c":3}

t2 = {"c":3,
     "d":4,
     "e":5}
h = {}

h.update(t2)
h["f"] = 6