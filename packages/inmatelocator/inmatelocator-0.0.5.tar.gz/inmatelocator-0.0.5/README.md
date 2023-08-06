Inmate Locator (ALPHA)
======================

This is a library and webservice for searching for people who are incarcerated
in the US.  It searches various individual state lookup services
simultaneously.

Working demo: https://inmatelocator.herokuapp.com

Most states (and the Federal Bureau of Prisons) have their own siloed web
services for searching for incarcerated people.  There is wide variation and
inconsistency among the interfaces and features they support.

This package aims to act as a compatibility layer and bridge.  It's
particularly important for service and support organizations that maintain
mailinglists of people in prison who frequently move.

Future goals for this service include:

 - adding more state backends
 - normalizing key data across states

Use as a library
----------------

To use this as a standalone library, install it with pip:

    pip install inmatelocator

TODO: documentation.  Basic usage:

    from inmatelocator.stateparsers import florida
    data = flroida.search(first_name="John", last_name="Dough")

Use as a web app
----------------

To use as a web servicde, clone the git repository and install dependencies
listed in ``requirements.txt``.

 - ``/``: HTML interface for querying the API.
 - ``/search/``: REST endpoint for querying. Returns JSON.
 
The search endpoint accepts the following parameters:

 - ``first_name``: String, part of first name to search for.
 - ``last_name``: String, part of last name to search for.
 - ``number``: String, the prisoner or DOC number assigned to the person.
 - ``state``: Which state to search in.

Different states have different minimum requirements for parameters -- for example, some require both first and last names in order to search by name.  

Data is returned in the following format:

    {
      "name": "<string>",   // the name of the person, if available
      "url": "<url>",       // a URL to the source for these results
      // Additional keys vary depending on the provider
    }

State parsers
-------------

The ``states/`` folder in the source repository contains parsers and lookup engines for each state.  Each parser should be named with a normalized lowercase name of the state with spaces removed, and should expose a ``search`` method that accepts the kwargs "first_name", "last_name", and "number".  It should return a dictionary with the following format:

    {
        'state': "<state name>",
        'results': [<array of search results>],
        'errors': [<array of errors encountered>],
        'url': "<url to state's search interface for humans>"
    }
