:mod:`xoutil.context` - Simple execution contexts
=================================================

.. automodule:: xoutil.context
   :members: context, Context


.. _context-greenlets:

.. note:: About thread-locals and contexts.

   The `context`:class: uses internally a `thread-local
   <threading.local>`:class: instance to keep context stacks in different
   threads from seeing each other.

   If `greenlet`:mod: is installed greenlet isolation is also warranted (which
   implies thread isolation).

   If you use collaborative multi-tasking based in other framework other than
   `greenlet`, you must ensure to monkey patch the `threading.local` class so
   that isolation is kept.

   In future releases of xoutil, we plan to provide a way to inject a
   "process" identity manager so that other frameworks be easily integrated.

   .. versionchanged:: 1.6.9 Added direct greenlet isolation and removed the
      need for `gevent.local`:mod:.

   .. versionadded:: 1.6.8 Uses `gevent.local`:mod: if available to isolate
      greenlets.
