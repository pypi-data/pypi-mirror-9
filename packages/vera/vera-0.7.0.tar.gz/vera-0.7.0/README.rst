|vera|

`vera <http://wq.io/vera>`__ is the reference implementation of the
Entity-Record-Attribute-Value (`ERAV <http://wq.io/docs/erav>`__) data
model. ERAV is an extension to Entity-Attribute-Value (EAV) that adds
support for maintaining multiple versions of an entity with different
provenance  [1]_.

|Build Status| |PyPI Package|

Tested on Python 2.7 and 3.4, with Django 1.6 and 1.7.

The implementation of ERAV provided by vera is optimized for storing and
tracking changes to *time series data* as it is exchanged between
disparate technical platforms (e.g. mobile devices, Excel spreadsheets,
and third-party databases). In this context, ERAV can be interpreted to
mean Event-Report-Attribute-Value, as it represents a series of *events*
being described by the *reports* submitted about them by various
contributors in e.g. an environmental monitoring or citizen science
project.

Getting Started
===============

.. code:: bash

    pip3 install vera

vera is an extension to `wq.db <http://wq.io/wq.db>`__, the database
component of the `wq framework <http://wq.io/>`__. See
https://github.com/wq/vera to report any issues.

Models
======

The core of vera is a collection of `Django
models <https://docs.djangoproject.com/en/1.7/topics/db/models/>`__ that
describe the various components of the ERAV data model. There are four
primary models (ERAV) and three auxilary models, for a total of seven
models. The mapping from vera models to their ERAV conceptual
equivalents is below:

+---------------------+-------------------+
| vera model          | ERAV equivalent   |
+=====================+===================+
| **``Event``**       | *Entity*          |
+---------------------+-------------------+
| ``Site``            | -                 |
+---------------------+-------------------+
| **``Report``**      | *Record*          |
+---------------------+-------------------+
| ``ReportStatus``    | -                 |
+---------------------+-------------------+
| **``Parameter``**   | *Attribute*       |
+---------------------+-------------------+
| **``Result``**      | *Value*           |
+---------------------+-------------------+
| ``EventResult``     | -                 |
+---------------------+-------------------+

The vera models are all
`swappable <https://github.com/wq/django-swappable-models>`__, which
means they can be subclassed and extended without breaking the foreign
key relationships needed by the ERAV model. For example, to customize
the ``Event`` model, subclass ``BaseEvent`` and update your
``settings.py``:

.. code:: python

    # myapp/models.py
    from wq.db.patterns import models
    from vera.models import BaseEvent

    class Event(BaseEvent):
        date = models.DateTimeField()
        type = models.CharField()

.. code:: python

    # settings.py
    WQ_EVENT_MODEL = "myapp.Event"

Each of the seven models are described in detail below.

``Event``
---------

The ``Event`` model corresponds to the *Entity* in the ERAV data model.
``Event`` represents a time series of monitoring events. For example,
each visit a volunteer makes to an observation site could be called an
``Event``. The ``Event`` model does not contain any metadata about the
digital record describing the event. This information is in the
``Report`` model, discussed below.

At a minimum, an Event instance has a ``site`` reference (see below) and
an event ``date``, which might be either a date or a full date and time,
depending on project needs. The default implementation assumes a date
without time. A custom ``date`` field and additional attributes can be
configured by extending ``BaseEvent`` and swapping out ``Event`` via the
``WQ_EVENT_MODEL`` setting. Note that if ``Event`` is swapped out,
``EventResult`` should be as well.

``Site``
--------

The ``Site`` model represents the location where an event occured. It is
not strictly a part of the original ERAV definition but is a natural
extension. In the default implementation, ``Site`` simply contains
``latitude`` and ``longitude`` fields. In practice, ``Site`` is often
swapped out for a version with `identify <http://wq.io/docs/identify>`__
support, to facilitate management of site identifiers assigned by the
project or by third parties.

.. code:: python

    # myapp/models.py
    from wq.db.patterns import models
    from vera.models import BaseSite

    class Site(models.IdentifiedModel, models.LocatedModel, BaseSite):
        pass

.. code:: python

    # settings.py
    WQ_SITE_MODEL = "myapp.Site"

All site instances have a ``valid_events`` property that returns all of
the event instances that contain at least one valid report.

``Report``
----------

The ``Report`` model corresponds to the *Record* in the ERAV data model.
``Report`` tracks the provenance metadata about the ``Event``, e.g. who
entered it, when it was entered, etc. Depending on when and how data is
entered, there can be multiple ``Reports`` describing the same event.
The status of each of these reports is tracked separately.

At a minimum, ``Report`` instances have an ``event`` attribute, a
``status`` attribute (see below), a ``user`` attribute, and an
``entered`` timestamp. ``user`` and ``entered`` are set automatically
when a report is created via the `REST
API <http://wq.io/docs/about-rest>`__. Additional attributes can be
added by extending ``BaseReport`` and swapping out ``Report`` via the
``WQ_REPORT_MODEL`` setting. Note that the ``Report`` model contains
only provenance metadata and no information about the event itself - the
``Event`` model should contain that information.

In addition to the default manager (``objects``), ``Report`` also has a
custom manager, ``vaild_objects`` that includes only reports with valid
statuses. ``Report`` instances have a ``vals`` property that can be used
to retrieve (and set) a ``dict`` mapping of parameter names to result
values (see below).

In cases where there are more than one valid report for an event, there
may be an ambiguity if reports contain contradicting data. In this case
the ``WQ_VALID_REPORT_ORDER`` setting can be used control which reports
are given priority. The default setting is ``("-entered", )``, which
gives priority to the most recently entered reports. (See the `CSCW
paper <http://wq.io/research/provenance>`__ for an in depth discussion
of conflicting reports).

``ReportStatus``
----------------

To support custom workflows, the list of report statuses is maintained
as a separate model, ``ReportStatus``. ``ReportStatus`` instances have a
short code (``slug``), a ``name``, and an ``is_valid`` boolean
indicating whether reports with that status should be considered valid.
Additional attributes can be added by extending ``BaseReportStatus`` and
swapping out ``ReportStatus`` via the ``WQ_REPORTSTATUS_MODEL`` setting.

In a typical project, the ``ReportStatus`` model might contain the
following instances:

+--------------+--------------+-------------+
| slug         | name         | is\_valid   |
+==============+==============+=============+
| unverified   | Unverified   | ``False``   |
+--------------+--------------+-------------+
| verified     | Verified     | ``True``    |
+--------------+--------------+-------------+
| deleted      | Deleted      | ``False``   |
+--------------+--------------+-------------+

``Parameter``
-------------

The ``Parameter`` model corresponds to the *Attribute* in the ERAV data
model. ``Parameter`` manages the definitions of the data "attributes"
(or "characteristics", or "fields") being tracked by the project. By
keeping these definitions in a separate table, the project can adapt to
new task definitions without needing a developer add columns to the
database.

At a minimum, ``Parameter`` instances have a ``name``, an ``is_numeric``
boolean, and a ``units`` definition (that usually only applies to
numeric parameters). Additional attributes can be added by extending
``BaseParameter`` and swapping out ``Parameter`` via the
``WQ_PARAMETER_MODEL`` setting. For streamlined integration with other
wq modules (in particular `dbio <http://wq.io/dbio>`__), the
``BaseParameter`` class leverages the
`identify <http://wq.io/docs/identify>`__ and
`relate <http://wq.io/docs/relate>`__ patterns.

``Result``
----------

The ``Result`` model corresponds to the *Value* in the ERAV data model.
``Result`` manages the definitions of the data attributes (or
characteristics, or fields) being tracked by the project. ``Result`` is
effectively a many-to-many relationship linking ``Report`` and
``Parameter`` with a value: e.g. "Report #123 has a Temperature value of
15". Note that ``Result`` does not link to ``Event`` directly - this is
a core distinction of the `ERAV <http://wq.io/docs/erav>`__ model.

At a minimum, ``Result`` instances have a ``type`` (which references
``Parameter``), a ``report``, and ``value_text`` and ``value_numeric``
fields - usually only one of which is set for a given ``Result``,
depending on the ``is_numeric`` property of the ``Parameter``.
``Result`` instances also contain an ``empty`` property to facilitate
fast filtering during analysis (see below). Additional attributes and
custom behavior can be added by extending ``BaseResult`` and swapping
out ``Result`` via the ``WQ_RESULT_MODEL`` setting. Note that if
``Result`` is swapped out, ``EventResult`` should be as well.

``Result`` instances have a settable ``value`` attribute which is
internally mapped to the ``value_text`` or ``value_numeric`` properties
depending on the ``Parameter``. ``Result`` instances also have an
``is_empty(val)`` method which is used to set the ``empty`` property.
The default implementation counts ``None``, empty strings, and strings
containing only whitespace as empty.

``EventResult``
---------------

The ``EventResult`` model is a
`denormalized <http://en.wikipedia.org/wiki/Denormalization>`__ table
containing data from the "active" results for all valid events. A valid
event is simply an event with at least one report with an ``is_valid``
``ReportStatus``. To determine which results are active:

1. First, all of the results are collected from all of the valid reports
   for each event. Only non-empty results are included.
2. Next, results are grouped by parameter. There can only be one active
   result per parameter.
3. Within each parameter group, the results are sorted by ``Report``,
   using the ``WQ_VALID_REPORT_ORDER`` setting. The first result in each
   group is the "active" result for that group.

(This is not exactly how the algorithm is implemented, but gives an idea
of how it works)

In the simple case, where there is only one valid ``Report`` for an
event, all of the ``Result`` instances from that ``Report`` will be
counted as active. In more complex situations, some ``Result`` instances
might be occluded.

Since this algorithm can be computationally expensive, the results are
stored in the ``EventResult`` model for fast retrieval. The
``EventResult`` model should never be modified directly, as it is
updated automatically whenever an ``Event``, ``Report``, or ``Result``
is updated.

The ``EventResult`` model contains an ``event`` attribute, a ``result``
attribute, and all of the fields from both ``Event`` and ``Result``
(prefixed with the source model name). The full set of fields for the
default ``EventResult`` model is ``event``, ``result``, ``event_site``,
``event_date``, ``result_type``, ``result_report``,
``result_value_numeric``, ``result_value_text``, and ``result_empty``.

Whenever ``Event`` or ``Result`` are swapped out, ``EventResult`` should
be swapped as well. The ``create_eventresult_model()`` function can be
used to generate an ``EventResult`` class without needing to manually
duplicate all of the field definitions.

.. code:: python

    # myapp/models.py
    from wq.db.patterns import models
    from vera.models import BaseEvent, Result

    class Event(BaseEvent):
        date = models.DateTimeField()
        type = models.CharField()
        
    EventResult = create_eventresult_model(Event, Result)

.. code:: python

    # settings.py
    WQ_EVENT_MODEL = "myapp.Event"
    WQ_EVENTRESULT_MODEL = "myapp.EventResult"

vera ships with an
`EventResultSerializer <https://github.com/wq/vera/blob/master/vera/serializers.py>`__
and views that leverage `wq.db chart <http://wq.io/docs/chart>`__'s
Pandas-based serializers. This makes it possible to quickly generate
d3.js charts from the ``EventResult`` table via
`wq/chart.js <http://wq.io/docs/chart-js>`__ and
`wq/pandas.js <http://wq.io/docs/pandas-js>`__.

.. [1]
   Sheppard, S. A., Wiggins, A., and Terveen, L. `Capturing Quality:
   Retaining Provenance for Curated Volunteer Monitoring
   Data <http://wq.io/research/provenance>`__. To appear in Proceedings
   of the 17th ACM Conference on Computer Supported Cooperative Work and
   Social Computing (CSCW 2014). ACM. February 2014.

.. |vera| image:: https://raw.github.com/wq/wq/master/images/256/vera.png
   :target: http://wq.io/vera
.. |Build Status| image:: https://travis-ci.org/wq/vera.svg?branch=master
   :target: https://travis-ci.org/wq/vera
.. |PyPI Package| image:: https://pypip.in/version/vera/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/vera
