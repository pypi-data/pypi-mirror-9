'''
env
===
Environment management tools.
'''
import os
import pickle
import collections
import sys
import glob


def _set_state(env, pypath):
    '''Restore environment and pythonpath to a previous state.

    :param env: Environment retrieved using os.environ.data.copy()
    :param pypath: PYTHONPATH retrieved from sys.path
    '''

    os.environ.data = env
    sys.path[:] = pypath


def _get_state():
    '''Retrieve the current environment and pythonpath

    :returns: Tuple containing copy of os.environ.data and sys.path
    '''

    return os.environ.data.copy(), sys.path[:]


def restore():
    '''Restore the environment to the state prior to running Wanderer'''

    wa_clean_env = os.environ['WA_CLEAN_ENV']

    decoded = pickle.loads(wa_clean_env)
    _set_state(*decoded)

    os.environ['WA_CLEAN_ENV'] = wa_clean_env

def save():
    '''Retrieve and store the current environment '''

    if not 'WA_CLEAN_ENV' in os.environ:
        os.environ['WA_CLEAN_ENV'] = pickle.dumps(_get_state())


def add_site_dir(path):
    '''Similar to site.addsitedir but inserts eggs and paths into sys.path
    instead of appending.
    '''

    if not os.path.exists(path):
        return

    for egg in glob.glob(path + '/*.egg'):
        egg_path = os.path.join(path, egg)
        if not egg_path in sys.path:
            sys.path.insert(1, os.path.join(path, egg))
    if not path in sys.path:
        sys.path.insert(1, path)


def from_dict(d):
    '''Sets environment variables defined in a dictionary. The dictionary
    should use lists to store multiple paths per environment variable. Any
    environment variables used in paths will be expanded. The PYTHONPATH
    variable will be independently parsed to insert any egg archives into
    sys.path.

    :param d: Environment dict
    '''

    # Handle os.environ
    for key, value in d.iteritems():
        path = None
        if isinstance(value, basestring):
            path = os.path.expandvars(value)
        elif isinstance(value, collections.Sequence):
            path = os.pathsep.join([os.path.expandvars(v) for v in value])
        else:
            raise  EnvironmentError(key + ' is not a string or list')

        try:
            os.environ[key] = path + os.pathsep + os.environ[key]
        except KeyError:
            os.environ[key] = path

    # Handle sys.path
    pypath = d.get('PYTHONPATH', None)
    if pypath:
        paths = []
        if isinstance(pypath, basestring):
            paths.append(os.path.expandvars(pypath))
        elif isinstance(pypath, collections.Sequence):
            paths.extend([os.path.expandvars(path) for path in pypath])
        else:
            raise  EnvironmentError(key + ' is not a string or list')

        for path in paths:
            add_site_dir(path)
