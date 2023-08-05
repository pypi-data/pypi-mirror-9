poplus-pci
==========

Generic python bindings to connect to the `Poplus components <http://poplus.org/components/>`_ APIs.

Actually, this is only a convenient wrapper around `Tortilla <https://github.com/redodo/tortilla>`_ generic
API wrapper, with some specialized instructions to use Poplus components apis.

The main advantage of Tortilla over other wrappers is that it allows access through a
full object oriented interface, both when requesting data, and when parsing the results.

Results are transformed from JSON into a Python dictionary, and then bunchified.

Installation
------------
poplus-pci is available as a module on PyPi, to install, simply run::

    pip install poplus-pci

Alternatively, you can clone this repo and install as you see fit.


Quick start
-----------

First, let's try read-only access to the ``legisladores-ar`` instance of Popit at mySociety,
and get the paged list of political organizations in the argentinian parliament:

.. code-block:: python

    from pci import Popit

    popit = Popit(
        instance='legisladores-ar',
        host='popit.mysociety.org',
    )

* ``instance`` Name of the instance you want to point to.
   There can be more than one for one installation.
* ``host`` The hostname of the PopIt server.

Once an instancehas been created, it's easy enough to access data,
using a full object oriented interface:

.. code-block:: python

    os = popit.organizations.get()

    # there are 65 organizations
    print(os.total)


    # but only 30 have been grabbed
    print(o.page)
    for i, o in enumerate(os.result, start=1):
        print("{0}: {1}".format(i, o.name))

    # how to get next page?
    print os.next_url

    # get it
    os = popit.organizations.get(params={'page': 2})


Write access (Popit)
--------------------

Make sure you have all the information you need. Then get the object use the `PopIt` constructor.

.. code-block:: python

    from pci import Popit

    popit = Popit(
        instance='openpolistest',
        host='popit.mysociety.org',
        api_key='-YOUR-API-KEY-',
    )

* ``api_key`` This is the API key you can request by clicking
  'Get API key' in the PopIt web interface for your instance, as
  `described in the documentation <http://popit.poplus.org/docs/api/#authentication>`_.

Then the basic CRUD operations will be:

.. code-block:: python


    # create
    einstein = popit.persons.post(data={
        'name': 'Albert Einstein',
        'links': [{
            'url': 'http://www.wikipedia.com/AlbertEinstein',
            'note': 'Wikipedia'
           }]
    })

    # read
    popit.persons(einstein.result.id).get()

    # update (note: is PUT, not PATCH)
    popit.persons(einstein.result.id).put(data={"name": "Albert Einstein"})

    # delete
    popit.persons(einstein.result.id).delete()


If you're still using an older PopIt instance and have not upgraded
your account for the new, more secure authentication system, instead
of ``api_key`` you can supply ``user`` and ``password``:

.. code-block:: python

    popit = Popit(
        instance='openpolistest',
        host='popit.mysociety.org',
        user='-USERNAME-',
        password='-PASSWORD-'
    )


* ``user`` Your username, the email address that you created the instance with
* ``password`` The password you were emailed when creating the instance



Popit Search api
----------------

Almost all APIs can be wrapped around the pci component, easily.

Starting from a popit instance, queries through the search API can be done:

.. code-block:: python

    popit.search.organizations.get(params={'q': 'trabajo'})
    popit.search.organizations.get(params={'q': 'trabajadores'})


Mapit access
------------

Mapit has read-only access, and the API does not adhere to REST standards.

The default Mapit instance is MySociety's Global Mapit:
http://global.mapit.mysociety.org/.

The mapit API call ``/point/SRID/LON,LAT/[box]``, can be invoked directly,
by tortilla wrapping utilities, or by using Mapit helpers.

.. code-block:: python

    mapit = Mapit()
    self.m.point.get('4326/12.5042,41.8981')
    self.m.areas_overpoint(lat='41.8981', lon='12.5042', srid='4326', box=True)

Other helpers are available, and will be implemented as needed in the futures.
You can find them in the ``pci/__init__.py`` file.



Requirements
------------

If you don't use pip to install the module, you'll also need:

* tortilla (``pip install tortilla``)


How to run the tests
--------------------

* Copy the file ``config_sample.py`` to ``config_test.py``
* Change the entries in ``config_test.py`` to refer to your test servers
* Install `oktest <http://www.kuwata-lab.com/oktest/>`_ (``pip install oktest``)
* Make sure components instances are running, and you have access to them.
  You cannot test this wrapper without running instances.
* run ``python test.py``to run all tests,
  ``python test_mapit.py``, or ``python test_popit.py`` to run the specified
  component's tests
