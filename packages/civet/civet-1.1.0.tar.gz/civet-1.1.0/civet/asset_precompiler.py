import atexit
from distutils.spawn import find_executable
import json
import os
import re
import signal
import subprocess
import sys

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from django.conf import settings
from django.contrib.staticfiles import finders
try:
    from django.utils.six.moves import _thread as thread
except ImportError:
    from django.utils.six.moves import _dummy_thread as thread

if not hasattr(settings, 'CIVET_PRECOMPILED_ASSET_DIR'):
    raise AssertionError(
        'Must specify CIVET_PRECOMPILED_ASSET_DIR in settings')

# The regex to find Sass if Bundler is used (see CIVET_BUNDLE_GEMFILE below)
BUNDLE_LIST_SASS_FINDER = re.compile(r'^.+?sass \(\d+\.\d+.+?\)', re.MULTILINE)

# Directory to put the compiled JavaScript and CSS files.
precompiled_assets_dir = settings.CIVET_PRECOMPILED_ASSET_DIR

# Default CoffeeScript arguments. Normally you shouldn't need to change.
coffee_arguments = getattr(
    settings, 'CIVET_COFFEE_SCRIPT_ARGUMENTS', ('--compile', '--map'))

# Default Sass arguments. If you use Compass, you will want to add
# `CIVET_SASS_ARGUMENTS = ('--compass',)` in your `settings.py`.
sass_arguments = getattr(
    settings, 'CIVET_SASS_ARGUMENTS', ())

# Location of `coffee`. By default, this will be the one found in $PATH.
coffee_bin = getattr(
    settings, 'CIVET_COFFEE_BIN', 'coffee')

# If given, Bundler (http://bundler.io/) will be used to invoke Sass
# (via `bundle exec sass`) with the designated Gemfile.
bundle_gemfile = getattr(
    settings, 'CIVET_BUNDLE_GEMFILE', None)

# Location of Bundler's `bundle`. This is used if settings.CIVET_BUNDLE_GEMFILE
# is given.
bundle_bin = getattr(
    settings, 'CIVET_BUNDLE_BIN', 'bundle')

# Location of `sass`. By default, this will be the one found in $PATH. If both
# settings.CIVET_BUNDLE_GEMFILE and settings.CIVET_SASS_BIN are set, an
# error will be raised when precompile_coffee_and_sass_assets() is called.
sass_bin = getattr(
    settings, 'CIVET_SASS_BIN', 'sass')

additional_ignore_patterns = getattr(
    settings, 'CIVET_IGNORE', None)


def precompile_and_watch_coffee_and_sass_assets():
    thread.start_new_thread(
        precompile_coffee_and_sass_assets, (), {
            'watch': True,
            'kill_on_error': True
        })


def precompile_coffee_and_sass_assets(watch=False, kill_on_error=False):
    """Precompile and watch all CoffeeScript and Sass files.

    This function has the side effect of adding precompiled_assets_dir to
    settings.STATICFILES_DIRS. Django's staticfiles library uses that list
    to serve static assets.

    Args:
        watch: If True, the method will continue watching for Sass and
            CoffeeScript source changes in the background.
        kill_on_error: If True, the method will trigger a signal before
            calling `sys.exit()`. If you call this method from the Django
            `runserver` management command, you need to use this so that you
            can correctly stop the command's loader thread.
    """

    def raise_error_or_kill():
        if kill_on_error:
            # Tell autoreload's loader thread that we're done
            os.kill(os.getpid(), signal.SIGINT)

            # Terminate the spawned server process
            sys.exit(1)
        else:
            raise AssertionError('Asset precompilation failed.')

    if not os.path.exists(precompiled_assets_dir):
        print 'Directory created for saving precompiled assets: %s' % (
            precompiled_assets_dir)
        os.makedirs(precompiled_assets_dir)

    if precompiled_assets_dir not in settings.STATICFILES_DIRS:
        settings.STATICFILES_DIRS += (precompiled_assets_dir,)

    coffee_files, sass_files = collect_coffee_and_sass_files()

    # Check if `coffee` or `sass` exists
    if coffee_files:
        if not find_executable(coffee_bin):
            if getattr(settings, 'CIVET_COFFEE_BIN', None):
                print >> sys.stderr, (
                    'Your project uses CoffeeScript, but "%s" in not '
                    'found.', coffee_bin)
            else:
                print >> sys.stderr, (
                    'Your project uses CoffeeScript, but "coffee" is not '
                    'found in your PATH.')
            raise_error_or_kill()

    if sass_files:
        # Make sure that CIVET_SASS_BIN and CIVET_BUNDLE_GEMFILE are not both
        # set in settings.
        if (getattr(settings, 'CIVET_SASS_BIN', None) and
                getattr(settings, 'CIVET_BUNDLE_GEMFILE', None)):
            print >> sys.stderr, (
                'CIVET_BUNDLE_GEMFILE and CIVET_SASS_BIN must not be set '
                'at the same time in settings.')
            raise_error_or_kill()

        if bundle_gemfile:
            if not find_executable(bundle_bin):
                print >> sys.stderr, (
                    'Your project uses Sass and you have specified a Gemfile '
                    'to be used with Bundler, but "bundle" is not found in '
                    'your PATH.')
                raise_error_or_kill()

            # Now, look for the gem `sass`.
            args = (bundle_bin, 'list')
            env = os.environ.copy()
            env['BUNDLE_GEMFILE'] = bundle_gemfile
            process = subprocess.Popen(args, stdout=subprocess.PIPE, env=env)
            stdout, _ = process.communicate()

            if process.returncode != 0:
                print >> sys.stderr, (
                    '"bundle list" failed, exit code = %d, messages:\n%s' % (
                        process.returncode,
                        '\n'.join("    %s" % ln for ln in stdout.split('\n'))))
                raise_error_or_kill()

            if not BUNDLE_LIST_SASS_FINDER.search(stdout):
                print >> sys.stderr, (
                    'You have specified to use Bundler to run Sass, but '
                    '"sass" is not included in your bundle.')
                raise_error_or_kill()

        elif not find_executable(sass_bin):
            if getattr(settings, 'CIVET_SASS_BIN', None):
                print >> sys.stderr, (
                    'Your project uses Sass, but "%s" is not found.' % (
                        sass_bin))
            else:
                print >> sys.stderr, (
                    'Your project uses Sass, but "sass" is not found in your '
                    'PATH.')
            raise_error_or_kill()

    try:
        if coffee_files:
            precompile_coffee(coffee_files, watch=watch)
        if sass_files:
            precompile_sass(sass_files, watch=watch)
    except subprocess.CalledProcessError:
        print >> sys.stderr, (
            'Imcomplete asset precompilation, server not started.')
        raise_error_or_kill()


def collect_src_dst_dir_mappings(src_dst_tuples):
    """Create a src_dir->dst_dir dict from a list of (src, dst) tuples.

    Args:
        src_dst_tuples: A list of (src, dst) tuples. For example, passing
            [('/some/source/test.coffee', '/some/output/test.js')] results
            in the dict {'/some/source': '/some/output'}.
    """
    return {os.path.dirname(src): os.path.dirname(dst)
            for src, dst in src_dst_tuples}


def compile_coffee(src, dst):
    """Compile CoffeeScript.

    Upon any compiler error, dst will be deleted if it exists. This prevents
    stale JS files from being served.
    """

    if os.path.exists(dst):
        if os.path.getmtime(dst) >= os.path.getmtime(src):
            return
        else:
            os.remove(dst)

    print 'Compiling %s' % src

    # coffee is smart enough to do mkdir -p for us
    dst_dir, dst_basename = os.path.split(dst)
    args = [coffee_bin, '-o', dst_dir]
    args.extend(coffee_arguments)
    args.append(src)
    subprocess.check_call(args)

    # check_call raises an exception if the exit status is not 0, so the fact
    # that we reach here means we can safely massage the map file.
    #
    # The reason we need to massage the map is that when `coffee -o` is used,
    # the sourceRoot and sources keys in the map become relative path
    # references, which are not valid paths from Django static file finder's
    # point of view.
    #
    # For example, if the JS file is at
    #
    #     /static/myapp/js/foo.js
    #
    # And the actual coffee source lives in
    #
    #     <source root>/myapp/static/myapp/js/foo.coffee
    #
    # Without the massaging, sourceRoot and sources in the map are:
    #
    #     {
    #         "sourceRoot": "../../..",
    #         "sources": ["myapp/static/myapp/js/foo.coffee"]
    #     }
    #
    # Which would make the browser want to fetch this:
    #
    #     /myapp/static/myapp/js/foo.coffee
    #
    # Which we know is wrong.
    #
    # By removing the relative references, the browser will correctly fetch
    #
    #     /static_files/myapp/js/foo.coffee
    #
    # Which will be found by Django's static finder correctly.
    map_filename = os.path.splitext(dst_basename)[0] + '.map'
    map_path = os.path.join(dst_dir, map_filename)

    if os.path.exists(map_path):
        map_data = None
        with open(map_path) as f:
            map_data = json.load(f)
            map_data['sourceRoot'] = ''
            map_data['sources'] = [os.path.basename(src)]

        with open(map_path, 'w') as f:
            json.dump(map_data, f)


def precompile_coffee(coffee_files, watch=False):
    """Pre-compile CoffeeScript source files and watch for changes.

    We have to roll our own watchdog-based solution because:

    1. Unlike sass, coffee does not allow watching multiple directories. This
       leaves us with only one option: Watch the entire project root
       directory. That is not viable because we use a different directory
       layout for the compiled assets (think how collectstatic works).
    2. coffee can't handle the number of source files we have! This is caused
       by the combination of node.js's FS watcher implementation and OS X's
       default limit on the number of open files. This can be mitigated by
       asking all our devs to remember to dial up the limit manually, but then
       again 1. makes it hard to work with. For details, see
       https://github.com/joyent/node/issues/2479
    """

    # Block and compile non-existent or newer files first
    print 'Start precompiling CoffeeScript files'
    for src, dst in coffee_files:
        compile_coffee(src, dst)
    print 'End precompiling CoffeeScript files'

    if not watch:
        return

    # Watch changes in directories containing CoffeeScript source files
    src_dst_dir_map = collect_src_dst_dir_mappings(coffee_files)
    observer = Observer()
    event_handler = CoffeeScriptFSEventHandler(src_dst_dir_map)

    for src_dir in src_dst_dir_map:
        observer.schedule(event_handler, src_dir, recursive=False)

    # The observer will start its own thread. We don't care about cleaning it
    # up since it goes down with the server's process. See
    # django.utils.autoreload.python_reloader
    print 'Start watching for CoffeeScript changes'
    observer.start()

    # Stop the observer when Django's autoreload calls sys.exit() before
    # reloading
    def cleanup():
        observer.stop()

    atexit.register(cleanup)


def get_shortest_topmost_directories(dirs):
    """Return the shortest topmost directories from the dirs list.

    Args:
        dirs: A list of directories

    Returns:
        The shortest list of parent directories s, such that every directory
        d in dirs can be reached from one (and only one) directory in s.

        For example, given the directories /a, /a/b, /a/b/c, /d/e, /f
        since /a/b and /a/b/c can all be reached from /a, only /a is needed.
        /d/e can only be reached from /d/e and /f from /f, so the resulting
        list is /a, /d/e, and /f.
    """

    if not dirs:
        return []

    # Sort the dirs and use path prefix to eliminate covered children
    sorted_dirs = sorted(dirs)

    current = sorted_dirs.pop(0)
    results = [current]

    # To avoid the case where /foobar is treated as a child of /foo, we add
    # the / terminal to each directory before comparison
    current = current + '/'

    while sorted_dirs:
        next = sorted_dirs.pop(0)
        terminated_next = next + '/'
        if not terminated_next.startswith(current):
            current = terminated_next
            results.append(next)
    return results


def precompile_sass(sass_files, watch=False):
    """Pre-compile Sass source files and watch for changes."""

    if bundle_gemfile:
        base_args = [bundle_bin, 'exec', 'sass']
        env = os.environ.copy()
        env['BUNDLE_GEMFILE'] = bundle_gemfile
    else:
        base_args = [sass_bin]
        env = None

    # Collect the directories we want to watch
    dir_map = collect_src_dst_dir_mappings(sass_files)

    # sass watch directories recursively, so we can remove children dirs.
    topmost_dirs = get_shortest_topmost_directories(dir_map)
    dir_map = {k: dir_map[k] for k in topmost_dirs}

    # sass can update and monitor multiple directories with the arguments
    # in the form of <src_dir_1>:<dst_dir_1> <src_dir_2>:<dst_dir_2> ...
    dir_pairs = [':'.join(item) for item in dir_map.iteritems()]

    # Block and compile non-existent or newer files first
    print 'Start precompiling Sass files'
    args = list(base_args)
    args.append('--update')
    args.extend(sass_arguments)
    args.extend(dir_pairs)
    process = subprocess.Popen(args, env=env)
    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(args[0], process.returncode)
    print 'End precompiling Sass files'

    if not watch:
        return

    # Start watching with a separate process
    args = list(base_args)
    args.append('--watch')
    args.extend(sass_arguments)
    args.extend(dir_pairs)
    process = subprocess.Popen(args, env=env, close_fds=True)

    # Django's autoreload calls sys.exit() before reloading, and we want to
    # kill the Sass process we've spawned at that point.
    def cleanup():
        process.kill()

    atexit.register(cleanup)


def is_coffee(src):
    return os.path.splitext(src)[1] == '.coffee'


class CoffeeScriptFSEventHandler(FileSystemEventHandler):
    """A watchdog FS event handler for watching CoffeeScript changes.

    We don't handle directory creation events anywhere in our source dir. We
    rarely add new directories, and when that happens, we can always re-start
    the runserver command. Handling directory events correctly will require
    more code than is practical.
    """

    def __init__(self, src_dst_dir_map):
        super(FileSystemEventHandler, self).__init__()
        self.src_dst_dir_map = src_dst_dir_map

    def get_dst_path(self, src_path):
        src_dir, src_filename = os.path.split(src_path)
        dst_dir = self.src_dst_dir_map.get(src_dir)
        if not dst_dir:
            return None
        dst_filename = os.path.splitext(src_filename)[0] + '.js'
        dst_path = os.path.join(dst_dir, dst_filename)
        return dst_path

    def compile(self, src_path):
        dst_path = self.get_dst_path(src_path)
        if not dst_path:
            print >> sys.stderr, (
                'Warning: No matching destination found for source {0}, and ' +
                'the source is not compiled').format(src_path)
        else:
            try:
                compile_coffee(src_path, dst_path)
            except subprocess.CalledProcessError:
                # coffee already reported the actual error to stderr
                pass

    def on_created(self, event):
        if event.is_directory:
            print >> sys.stderr,  (
                'Warning: New directory %s created but not watched' %
                event.src_path)
        elif is_coffee(event.src_path):
            self.compile(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            print >> sys.stderr,  (
                'Warning: Directory %s deleted' % event.src_path)
        elif is_coffee(event.src_path):
            print >> sys.stderr,  'Warning: File %s deleted' % event.src_path

    def on_modified(self, event):
        if not event.is_directory and is_coffee(event.src_path):
            self.compile(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            print >> sys.stderr,  (
                'Warning: Directory %s deleted' % event.src_path)
        elif is_coffee(event.src_path) and is_coffee(event.dest_path):
            print >> sys.stderr,  (
                'Warning: File renamed {0} -> {1}'.format(
                    event.src_path, event.dest_path))
            self.compile(event.dest_path)


def collect_coffee_and_sass_files():
    """Collect .coffee and .scss/.sass files across the project

    This is a mini implementation of the "collectstatic" management command.

    Returns:
        A tuple of two lists (sass_files, coffee_files). Each list consists of
        the tuples (src_path, dst_path).
    """

    # This common ignore pattern is defined inline in
    # django.contrib.staticfiles.management.commands.collectstatic, and we
    # just repeat it here verbatim
    ignore_patterns = ['CVS', '.*', '*~']

    if additional_ignore_patterns:
      ignore_patterns.extend(additional_ignore_patterns)

    def get_output_path(base, ext):
        return os.path.join(precompiled_assets_dir, base + ext)

    sass_files = []
    coffee_files = []

    # staticfiles has two default finders, one for the STATICFILES_DIRS and
    # one for the /static directories of the apps listed in INSTALLED_APPS.
    # This allows us to discover all the files we are interested in across
    # the entire project, including the libraries it uses.
    for finder in finders.get_finders():
        for partial_path, storage in finder.list(ignore_patterns):
            # Get the actual path of the asset
            full_path = storage.path(partial_path)

            # Resolve symbolic links
            src_path = os.path.realpath(full_path)

            base, ext = os.path.splitext(partial_path)
            if ext == '.coffee':
                coffee_files.append((src_path, get_output_path(base, '.js')))
            elif ext == '.scss' or ext == '.sass':
                sass_files.append((src_path, get_output_path(base, '.css')))

    return coffee_files, sass_files
