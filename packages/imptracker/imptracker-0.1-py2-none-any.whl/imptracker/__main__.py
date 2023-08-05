# coding: utf-8

import os
import sys

from . import _base


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--save-pickle":
        pickle_out = sys.argv[2]
        sys.argv[1:3] = []
    else:
        pickle_out = None

    progname = sys.argv[1]
    sys.argv[1:2] = []

    sys.path.insert(0, os.path.dirname(progname))
    with open(progname, 'rb') as fp:
        code = compile(fp.read(), progname, 'exec')
        globs = {
            '__file__': progname,
            '__name__': '__main__',
            '__package__': None,
        }

    _base._logged_dependencies["__main__"] = []
    try:
        exec code in globs, None
    finally:
        d = dict((k, list(v)) for (k, v) in _base.get_logged_dependencies().iteritems())
        _base.report_logged_dependencies()
        if pickle_out:
            import pickle
            log = _base.ImportLog(d)
            s = pickle.dumps(log, pickle.HIGHEST_PROTOCOL)
            open(pickle_out, "wb").write(s)


if __name__ == "__main__":
    main()
