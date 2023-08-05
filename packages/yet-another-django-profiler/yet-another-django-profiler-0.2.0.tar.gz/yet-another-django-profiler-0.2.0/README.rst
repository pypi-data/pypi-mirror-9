yet-another-django-profiler README
==================================

Yet Another Django Profiler attempts to combine the best features of assorted
other Django profiling middleware classes that have been created over the
years.  (For more background information, see my
`blog post <http://blog.safariflow.com/2013/11/21/profiling-django-via-middleware/>`_
on the topic.)

Installation
------------
First, get the code via pip install::

    pip install yet-another-django-profiler

Then add ``yet_another_django_profiler.middleware.ProfilerMiddleware`` to your
``MIDDLEWARE_CLASSES`` Django setting (typically at the end of the list, if
you want to include profiling data on the other middleware that's in use).
If you want to generate call graphs with the middleware, you also need to
install `Graphviz <http://www.graphviz.org/Download.php>`_.

Usage
-----
The simplest usage is to just add a ``profile`` parameter to the URL of a
Django view.  This uses Graphviz to generate a PDF representation of the call
graph for the code executed to perform the view, and returns that as the
response to the request instead of the rendered view itself.  So calling a
URL like ``http://localhost:8000/admin/?profile`` shows a PDF like
`this <https://github.com/safarijv/yet-another-django-profiler/blob/master/docs/admin_call_graph.pdf?raw=true>`_
in the browser.

Alternatively, you can display a table of called functions ordered by the
desired statistic by using a URL such as ``http://localhost:8000/?profile=time``.
The available sorting options are:

* ``calls`` (call count)

* ``cumulative`` (cumulative time)

* ``file`` (file name, same as ``module``)

* ``module`` (file name, same as ``file``)

* ``pcalls`` (primitive call count)

* ``line`` (line number)

* ``name`` (function name)

* ``nfl`` ( function name/file/line)

* ``stdname`` (standard name)

* ``time`` (internal time)

By default, only the top 20% of function calls are included in the table.  To
change that, add a ``fraction`` parameter with the desired display ratio
(hence the default value is ``fraction=.2``).  Alternatively, you can
instead specify a maximum number of function calls to display using the
``max_calls`` parameter.  And if you specify a regular expression with the
``pattern`` parameter, only calls of functions whose names match the
specified pattern will be displayed.  (I'd recommend sticking to basic
sub-strings unless you really enjoy figuring out how to URL-escape special
characters.)

If you forget the available sorting options and such, you can use
``profile=help`` as a request parameter to display the usage instructions in
the browser.

Settings
--------
The middleware is designed to be available whenever the ``DEBUG`` setting is
True, and removes itself from the middleware chain otherwise (so it can safely
be left in the dependencies for production deployments without performance or
security problems).  If for some reason you want to change this behavior, you
can set the ``YADP_ENABLED`` boolean setting directly to determine whether the
middleware is active or not.

If you have pages where the default profiling parameter names conflict with
existing parameters in the application, you can choose different ones via the
following settings:

* ``YADP_PROFILE_PARAMETER`` (default is "profile")

* ``YADP_FRACTION_PARAMETER`` (default is "fraction")

* ``YADP_MAX_CALLS_PARAMETER`` (default is "max_calls")

* ``YADP_PATTERN_PARAMETER`` (default is "pattern")

In order to get simple and meaningful profiling data, a
`few other changes <https://github.com/safarijv/yet-another-django-profiler/blob/master/docs/settings.rst>`_
to your settings may be in order.
