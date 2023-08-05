Civet
=====

![alt text](http://upload.wikimedia.org/wikipedia/commons/2/28/Luwak-Katze_in_Kepahiang.jpg "Civet")

(Picture credit: [Leendertz](http://en.wikipedia.org/wiki/Kopi_Luwak#mediaviewer/File:Luwak-Katze_in_Kepahiang.jpg))

Civet precompiles Sass and CoffeeScript files in your Django project when
you use the `runserver` command. It will also watch the file changes for you.
Therefore, you can edit your Sass and CoffeeScript files and expect
`runserver` to recompile those files upon save, just like it how restarts the
app server when you make changes to your Python source code


Usage
-----

In your `settings.py`, add Civet to your `INSTALLED_APPS` right after
`django.contrib.staticfiles`:

    INSTALLED_APPS = (
        # ...
        'django.contrib.staticfiles',
        'civet',
        # ...
    )

Then add a `CIVET_PRECOMPILED_ASSET_DIR` setting that tells Civet where to
put the precompiled assets. For example:

    CIVET_PRECOMPILED_ASSET_DIR = os.path.join(BASE_DIR, 'precompiled_assets')

That's it. Once set up, each time you use `manage.py runserver`, Civet will
first check to see if there are new Sass and CoffeeScript files that need
precompiling. It will also start watch for file changes.


Sass and CoffeeScript Versions Supported
----------------------------------------

Civet is known to work with the following versions of Sass and CoffeeScript:

* Sass 3.2.5+ and Compass 0.12.2+
* CoffeeScript 1.6.3+


"But We Only Use Sass (or CoffeeScript)"
----------------------------------------

If your project doesn't use Sass and therefore doesn't contain any Sass files,
Civet won't invoke the Sass compiler and therefore it's ok if you don't have
Sass installed. The same rule applies to CoffeeScript files.


Customizable Options
--------------------

By default, Civet looks for `coffee` and `sass` in your `PATH` environment
varible. If you want to use specific paths, you can put these in your
`settings.py`:

    # The paths here are just examples
    CIVET_COFFEE_BIN = '/opt/local/bin/coffee'
    CIVET_SASS_BIN = '/opt/local/bin/sass'

For Sass, a lot of people use [Bundler](http://bundler.io/) to manage their
Ruby command-line tools. This can be especially useful if you also use
libaries like Compass and want to lock down their versions. Bundler requires
you to set up a `Gemfile`. To use Bundler to run Sass, add this in your
`settings.py`:

    CIVET_BUNDLE_GEMFILE = '/some/where/Gemfile'

Please note that `CIVET_BUNDLE_GEMFILE` and `CIVET_SASS_BIN` must not be set
at the same time. If both are set, Civet will raise an error. Also, by
default, Civet looks for the tool `bundle` in your `PATH`. If you want to
use a specific path, set `CIVET_BUNDLE_BIN` in your `settings.py`.

Finally, if you want to use additional CoffeeScript or Sass compiling options,
add these to your `settings.py`. Here are the default values Civet uses:

    CIVET_COFFEE_SCRIPT_ARGUMENTS = ('--compile', '--map')
    CIVET_SASS_ARGUMENTS = ()

If you want to, for example, use Compass with Sass, use:

    CIVET_SASS_ARGUMENTS = ('--compass',)

You can also define patterns (files or directories) for Civet to ignore by
setting:

    # As an exmaple, this will cause Civet to ignore files with 'coffee' in the
    # name or path.
    CIVET_IGNORE_PATTERNS = ['coffee']

This gets extended into the ignore_patterns list defined in
`django.contrib.staticfiles.management.commands.collectstatic`.

You can also define staticfile directories you want Civet to ignore by setting:

    # This will cause Civet to ignore files located in 'bower_components' or
    # 'node_modules' even if those folders are included in STATICFILES_DIRS.
    CIVET_IGNORE_DIRS = ['bower_components', 'node_modules']


This is particularly useful when using a package manager such as [Bower](http://bower.io/)
or [NPM](https://www.npmjs.com/).  These managers often install packages that
include their own build systems, configurations, and files that are incompatible
with how Civet compiles assets.

Recompile Everything
--------------------

To recompile everything, just quit the server, delete the entire
`CIVET_PRECOMPILED_ASSET_DIR` directory, and use the `runserver` command
again.


Sample Project
--------------

We have included a sample project in `testsite/` to demonstrate how Civet
works with Django.


Motivation
----------

We have developed Civet to solve the following problems:

1. It is too cumbersome to ask all our developers to remember using
   `coffee -w` and `sass -w` every time they use `runserver`.

2. We want our CoffeeScript and Sass assets to be precompiled. It makes no
   sense to compile them on the fly as we serve static assets. Plus, Sass
   files that have a lot of includes can take a long time to process.
   At one point we had a Sass file that took 6 seconds to compile. We don't
   want our developers to wait for 6 seconds every time they reload a page.

3. Django's static file layout requires Sass and CoffeeScript to watch
   for separate directories. We simply can't have them watch the top-level
   directory and call it a day. It is very cumbersome, however, to have
   Sass compiler watch multiple directories, and the option for
   multi-directory watch simply doesn't exist in the CoffeeScript compiler.

4. We have a lot of CoffeeScript files, and on OS X that number exceeds the
   default maximum number of files that node.js (on which the official
   CoffeeScript compiler is based on) can watch. (See
   [this issue](https://github.com/joyent/node/issues/2479) for details.)


About the Name
--------------

Civet is "a slender nocturnal carnivorous mammal" (according to *New Oxford
American Dictionary*) that also produces
[kopi luwak](http://en.wikipedia.org/wiki/Kopi_Luwak) by ingesting coffee
beans. I was looking for a cheeky (sassy) project name that has to do with
coffee, and this comes to mind. Disclaimer: I have no idea what kopi luwak
tastes like, and no animal is harmed during the development of this plug-in.
