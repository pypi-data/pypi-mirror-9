
# Ensure that the module structure is correct.
# This cannot be run in a function, so pytest beware!

def test_import_star():
    exec("from yter import *")
