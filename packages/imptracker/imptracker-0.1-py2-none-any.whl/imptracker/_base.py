"""
Imports Logger: Tracks all imports and computes *actual* module dependencies.
"""

# These aren't logged...

import os
import imp
import sys
import __builtin__


# Wrap the builtin __import__ function to find out when a module requests
# another module to get imported. This won't track any C extension
# dependencies though.

def _wrap_builtin_import():
    builtin_import = __import__
    def logging_import(name, globals=None, locals=None, fromlist=None, level=-1):
        import_result = builtin_import(name, globals, locals, fromlist, level)
        caller_module = sys._getframe(1).f_globals["__name__"]
        _logged_dependencies.setdefault(caller_module, []).append(import_result.__name__)

        # import a.b.c returns a but is actually a dependency on a, a.b and a.b.c
        if not fromlist and "." in name:
            subimports = name.split(".")[1:]
            t = import_result.__name__
            while subimports:
                t += "." + subimports.pop(0)
                _logged_dependencies[caller_module].append(t)

        # Capture module imports via "from package import module" by looking for module
        # objects in import_result.

        if fromlist:
            if '*' in fromlist:
                fromlist = list(fromlist) + list(getattr(import_result, "__all__", []))
            for fromname in fromlist:
                t = getattr(import_result, fromname, None)
                # check if the name in fromlist refers to a module
                if type(t) == type(import_result):
                    _logged_dependencies[caller_module].append(t.__name__)
        return import_result

    return logging_import

__builtin__.__import__ = _wrap_builtin_import()
del _wrap_builtin_import


# Import dependencies logged so far. Maps module names to a set of requested
# module names. Use get_logged_dependencies() to get a copy of this information.

_logged_dependencies = {}



def get_logged_dependencies():
    """
    Returns a dictionary mapping module names to the sets of required modules
    they imported.
    """
    return dict(_logged_dependencies)


def report_logged_dependencies(stream=None):
    if stream is None:
        stream = sys.stderr

    print >>stream, "Import dependencies:\n"

    for name in sorted(_logged_dependencies):
        print >>stream, "Required by {0}:".format(name)

        pos = 0
        first = True

        for dependency in _logged_dependencies[name]:
            if pos == 0:
                stream.write("    ")
                pos = 4
            else:
                stream.write(", ")
                pos += 2

            if pos + len(dependency) > 78 and not first:
                stream.write("\n    ")
                first = True
                pos = 4

            stream.write(dependency)
            pos += len(dependency)
            first = False

        stream.write("\n\n")


class ImportLog(object):

    def __init__(self, logged_requests):
        self._logged_requests = dict(logged_requests)

    def get_module_imports(self, module_name):
        """
        List the names of all modules requested by a given module. If the
        module is not known, an empty list is returned.

        :rtype: [str]
        :return: List of requested modules.
        """
        return list(self._logged_requests.get(module_name, []))
