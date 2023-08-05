=========
 hatcher
=========

Surprisingly, a client to talk to the brood server.


Getting started for development
===============================

In order to run tests, the development requirements are required::

    $ pip install -r dev_requirements.txt


Basic Usage
===========

When used in production, the latest **release** tag must be used. For example, a
tag such as ``v0.3.0`` must be used, rather than ``v0.4.0.dev419``.

To get a basic idea of usage::

    python -m hatcher --help

To upload an egg::

    # Upload a free rh5-32 egg
    python -m hatcher --url http://brood-dev upload_egg enthought dev rh5-32 some_egg.egg

To list existing eggs in a repo::

    # Upload a free rh5-32 egg
    python -m hatcher --url http://brood-dev list_eggs enthought dev rh5-32

To create a new repository and upload eggs to it::

    # List the repositories
    python -m hatcher --url http://brood-dev list_repositories enthought
    # Create a new repository
    python -m hatcher --url http://brood-dev create_repository enthought \
        geocanopy_dev "the official geocanopy_dev repository7"
    # Push some new eggs
    python -m hatcher --url http://brood-dev batch_upload_eggs enthought \
        geocanopy_dev win-32 <some_directory_with_eggs_in_it>
    # Delete the repository (fails by default if not empty, use --force to
    # force the deletion)
    python -m hatcher --url http://brood-dev delete_repository enthought \
        geocanopy_dev
