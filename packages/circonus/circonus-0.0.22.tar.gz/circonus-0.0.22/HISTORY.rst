Release History
---------------

0.0.22 (2015-02-14)
+++++++++++++++++++

**Bug fixes**

- Avoid selecting ``df`` metrics other than ``df_complex`` when creating disk
  free graphs.

0.0.21 (2015-01-29)
+++++++++++++++++++

**Improvements**

- Change the ``collectd`` client interface to take an explicit check bundle to
  create graphs from rather than naïvely using the *first* ``collectd`` check
  bundle found for ``target``.

- Refactor the ``datetime_to_int`` method from ``Annotation`` to be a function
  in ``util``.

0.0.20 (2015-01-28)
+++++++++++++++++++

**Bug fixes**

- Remove errant ``df`` from custom graph title.

0.0.19 (2015-01-28)
+++++++++++++++++++

**Bug fixes**

- Fix optional custom titles for all ``collectd`` graphs.

0.0.18 (2015-01-26)
+++++++++++++++++++

**Improvements**

- Add optional custom titles for all ``collectd`` graphs.

0.0.17 (2015-01-26)
+++++++++++++++++++

**Improvements**

- Add function for updating the ``status`` of each metric in a list of
  metrics.

0.0.16 (2015-01-24)
+++++++++++++++++++

**Improvements**

- Make the ``get_tag_string`` function public.

0.0.15 (2015-01-24)
+++++++++++++++++++

**Bug fixes**

- Add ``MANIFEST.in`` to include required distribution files.

0.0.14 (2015-01-22)
+++++++++++++++++++

**Bug fixes**

- Hard code version in setup to avoid setup dependency

0.0.13 (2015-01-22)
+++++++++++++++++++

**Bug fixes**

- Require the ``colour`` package at setup time

0.0.12 (2015-01-22)
+++++++++++++++++++

**Improvements**

- Add client method to create all supported collectd plugin graphs for a
  specific target at once.
- Update ``circonus.collectd.cpu`` API to act like the other plugin modules.
- Change exception handling to raise HTTPError in log decorator.
- Add API documentation

0.0.11 (2015-01-21)
+++++++++++++++++++

**Improvements**

- Add collectd df graph
- Add API documentation

0.0.10 (2015-01-20)
+++++++++++++++++++

**Improvements**

- Rename ``circonus.collectd.network`` to ``circonus.collectd.interface`` to
  reflect what the name of the ``collectd`` module is.

0.0.9 (2015-01-20)
++++++++++++++++++

**Improvements**

- Add collectd network graph
- Add API documentation

0.0.8 (2015-01-20)
++++++++++++++++++

**Improvements**

- Add collectd memory graph
- Add API documentation

**Bug fixes**

- Fix key error when looking for metrics in a check bundle that has none.
- Handle error state when sorting metrics.  If there were less metrics than
  suffixes to sort by the returned list would contain ``None`` values.  Now an
  empty list is returned.

0.0.7 (2015-01-19)
++++++++++++++++++

**Improvements**

- Add initial support for collectd
- Add graph module
- Add metric module
- Add API documentation

0.0.6 (2015-01-16)
++++++++++++++++++

**Improvements**

- Add optional common tags parameter to CirconusClient class for a cleaner way
  to specify common tags on a given instance of the client.
- Update all docstrings to reStructuredText format with parameter and return
  types.
- Add API documentation.

0.0.5 (2015-01-13)
++++++++++++++++++

**Bug fixes**

- Fix documentation link

0.0.4 (2015-01-13)
++++++++++++++++++

**Improvements**

- Documentation

0.0.3 (2015-01-13)
++++++++++++++++++

**Bug fixes**

- Make the ``with_common_tags`` decorator copy the ``COMMON_TAGS`` list rather
  than modify it.

0.0.2 (2015-01-13)
++++++++++++++++++

**Improvements**

- Annotation decorator, context manager & ad hoc methods
- ``HISTORY.rst``

**Bug fixes**

- Properly unpack ``args`` in ``with_common_tags`` decorator

0.0.1 (2015-01-08)
++++++++++++++++++

- Wrap REST API with requests
- Custom HTTP request headers for app. name and token
- Resource tagging
- Error logging
