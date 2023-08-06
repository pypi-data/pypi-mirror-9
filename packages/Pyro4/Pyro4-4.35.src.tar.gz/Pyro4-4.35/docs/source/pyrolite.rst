.. index:: Pyrolite, Java, .NET, C#

*******************************************
Pyrolite - client library for Java and .NET
*******************************************

This library allows your Java or .NET program to interface very easily with
the Python world. It uses the Pyro protocol to call methods on remote
objects. It also supports convenient access to a Pyro Flame server including the remote
interactive console.

Pyrolite is a tiny library that implements a part of the client side Pyro library,
hence its name 'lite'.  Pyrolite has no additional dependencies.
So if you don't need Pyro's full feature set, and don't require your
Java/.NET code to host Pyro objects itself, Pyrolite may be
a good choice to connect java or .NET and python.

Pyrolite also contains a feature complete implementation of Python's :mod:`pickle` protocol
(with fairly intelligent mapping of datatypes between Python and Java/.NET),
and a small part of Pyro's client network protocol and proxy logic. It can  use
the Serpent serialization format as well.


Get it from here: http://irmen.home.xs4all.nl/pyrolite/

Readme: http://irmen.home.xs4all.nl/pyrolite/README.txt

License (same as Pyro): http://irmen.home.xs4all.nl/pyrolite/LICENSE

Source is on Github: https://github.com/irmen/Pyrolite

Small code example in Java:

.. code-block:: java

    import net.razorvine.pyro.*;

    NameServerProxy ns = NameServerProxy.locateNS(null);
    PyroProxy remoteobject = new PyroProxy(ns.lookup("Your.Pyro.Object"));
    Object result = remoteobject.call("pythonmethod", 42, "hello", new int[]{1,2,3});
    String message = (String)result;  // cast to the type that 'pythonmethod' returns
    System.out.println("result message="+message);
    remoteobject.close();
    ns.close();

The same example in C#:

.. code-block:: csharp

    using Razorvine.Pyro;

    using( NameServerProxy ns = NameServerProxy.locateNS(null) )
    {
        using( PyroProxy something = new PyroProxy(ns.lookup("Your.Pyro.Object")) )
        {
            object result = something.call("pythonmethod", 42, "hello", new int[]{1,2,3});
            string message = (string)result;  // cast to the type that 'pythonmethod' returns
            Console.WriteLine("result message="+message);
        }
    }

You can also use Pyro Flame rather conveniently because of some wrapper classes:

.. code-block:: java

    Config.SERIALIZER = Config.SerializerType.pickle;   // flame requires the pickle serializer
    PyroProxy flame = new PyroProxy(hostname, port, "Pyro.Flame");
    FlameModule r_module = (FlameModule) flame.call("module", "socket");
    System.out.println("hostname=" + r_module.call("gethostname"));

    FlameRemoteConsole console = (FlameRemoteConsole) flame.call("console");
    console.interact();
    console.close();

