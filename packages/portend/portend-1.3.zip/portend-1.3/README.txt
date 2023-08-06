portend
=======

por·tend
pôrˈtend/
verb

    be a sign or warning that (something, especially something momentous or calamitous) is likely to happen.

Usage
-----

Use portend to monitor TCP ports for bound or unbound states.

For example, to wait for a port to be occupied, timing out after 3 seconds::

    portend.occupied('www.google.com', 80, timeout=3)

Or to wait for a port to be free, timing out after 5 seconds::

    portend.free('::1', 80, timeout=5)

The portend may also be executed directly. If the function succeeds, it
returns nothing and exits with a status of 0. If it fails, it prints a
message and exits with a status of 1. For example::

    python -m portend localhost:31923 free
    (exits immediately)

    python -m portend -t 1 localhost:31923 occupied
    (one second passes)
    Port 31923 not bound on localhost.

Portend also exposes a ``find_available_local_port`` for identifying
a suitable port for binding locally::

    port = portend.find_available_local_port()
    print(port, "is available for binding")
