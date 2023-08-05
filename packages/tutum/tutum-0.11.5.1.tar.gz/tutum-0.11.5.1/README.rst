tutum
=====

CLI for Tutum. Full documentation available at `https://docs.tutum.co/v2/api/?shell# <https://docs.tutum.co/v2/api/?shell#>`_


Installing the CLI
------------------

In order to install the Tutum CLI, you can use ``pip install``:

.. sourcecode:: bash

    pip install tutum

For Mac OS users, you can use ``brew install``:

.. sourcecode:: bash

    brew install tutum

Now you can start using it:

.. sourcecode:: none

    $ tutum
    
    usage: tutum [-h] [-v]
             {build,container,image,login,node,nodecluster,service} ...

    Tutum's CLI
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
    
    Tutum's CLI commands:
      {build,container,image,login,node,nodecluster,service}
        build               Build an image using an existing Dockerfile, or create
                            one using buildstep
        container           Container-related operations
        image               Image-related operations
        login               Login into Tutum
        node                Node-related operations
        nodecluster         NodeCluster-related operations
        service             Service-related operations



Docker image
^^^^^^^^^^^^

You can also install the CLI via Docker:

.. sourcecode:: bash

    docker run tutum/cli -h

You will have to pass your username and API key as environment variables, as the credentials stored via ``tutum login``
will not persist by default:

.. sourcecode:: bash

    docker run -e TUTUM_USER=username -e TUTUM_APIKEY=apikey tutum/cli service

To make things easier, you might want to use an ``alias`` for it:

.. sourcecode:: bash

    alias tutum="docker run -e TUTUM_USER=username -e TUTUM_APIKEY=apikey tutum/cli"
    tutum service


Authentication
--------------

In other to manage your apps and containers running on Tutum, you need to log into Tutum in any of the following ways
(will be used in this order):

* Login using Tutum CLI or storing it directly in a configuration file in ``~/.tutum``:

.. sourcecode:: bash

    $ tutum login
    Username: admin
    Password:
    Login succeeded!

Your login credentials will be stored in ``~/.tutum``:

.. sourcecode:: ini

    [auth]
    user = "username"
    apikey = "apikey"

* Set the environment variables ``TUTUM_USER`` and ``TUTUM_APIKEY``:

.. sourcecode:: bash

    export TUTUM_USER=username
    export TUTUM_APIKEY=apikey
