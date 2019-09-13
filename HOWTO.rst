
using VisibleObject
-------------------

We give a simple example of a everyday network of objects.

Background is a framework to build a schedule of classes in a school.
First we introduce **Student**, **Teacher** and **ClassRoom** as basic items.

Then we add container (lists) of them. And finally a **Lesson** as a *struct* with a **Teacher**, a **ClassRoom** and a list of **Student**.

A list of **Lesson** gives a **Schedule** and
lists of **Student**, **Teacher** and **ClassRoom** together with a **schedule** build a **School**.

.. see absolute path doc/demo_visible_object.py

.. include:: ../demo_visible_object.py
   :code: python


setup a web api service
-----------------------

The second demo shows how to build a simple web service.

.. see absolute path doc/demo_server.py

.. include:: ../demo_server.py
   :code: python

