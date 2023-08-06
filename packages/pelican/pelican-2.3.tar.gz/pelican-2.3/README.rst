Pelican
#######

Pelican is a simple weblog generator, writen in python.

* Write your weblog entries directly with your editor of choice (vim!) and
  directly in restructured text.
* A simple cli-tool to (re)generate the weblog.
* Easy to interface with DVCSes and web hooks
* Completely static output, so easy to host anywhere !

Files metadatas
---------------

Pelican tries to be smart enough to get the informations he needs from the
filesystem (for instance, about the category of your articles), but you need to
provide by hand some of those informations in your files.

You could provide the metadata in the restructured text files, using the
following syntax::

    My super title
    ##############

    :date: 2010-10-03 10:20
    :tags: thats, awesome
    :category: yeah
    :author: Alexis Metaireau

Note that only the `date` metadata is mandatory, so you just have to add that in i
your files. The category can also be determined by the directory where the rst file
is. For instance, the category of `python/foobar/myfoobar.rst` is `foobar`.

Getting started — Generate your blog
-------------------------------------

Yeah? You're ready? Let's go ! You can install pelican in a lot of different
ways, the simpler one is via pip::

    $ pip install pelican

Then, you have just to launch pelican, like this::

    $ pelican /path/to/your/content/

And… that's all! You can see your weblog generated on the content/ folder.

This one will just generate a simple output, with the default theme. It's not
really sexy, as it's a simple HTML output (without any style). 

You can create your own style if you want, have a look to the help to see all
the options you can use::

    $ pelican --help

Why the name "Pelican" ?
------------------------

Heh, you didnt noticed? "Pelican" is an anagram for "Calepin" ;)

Source code
-----------

You can access the source code via mercurial at http://hg.notmyidea.org/pelican/
or via git on http://github.com/ametaireau/pelican/

Feedback !
----------

If you want to see new features in Pelican, dont hesitate to tell me, to clone
the repository, etc. That's open source, dude!

Contact me at "alexis at notmyidea dot org" for any request/feedback !
