olimex-ekg-emg
==============

|docs|

A Python package for gathering and viewing data from the `Olimex EKG/EMG Shield`_.


NOTICE
------

THIS SOFTWARE DOES NOT PROVIDE MEDICAL ADVICE

The information provided by this software is not medical advice. By using this software,
You acknowledge that this software does not and should not be construed to provide
health-related or medical advice, or clinical decision support, or to provide,
support or replace any diagnosis, recommendation, advice, treatment or decision by an
appropriately trained and licensed physician, or to create a patient-physician relationship.
You hereby agree that this software will not be relied on or used, in whole or in part,
for any of the preceding purposes by or on Your behalf with respect to any individual(s).
If You believe You suffer from any medical condition, whether or not this software's
results support this belief, You should immediately seek professional medical advice
or consult with a qualified medical professional.


Installation
------------

::

    pip install olimex-ekg-emg


Usage
-----

::

    >>> from olimex.gui import show_exg
    >>> show_exg('/path/to/port')

Replace ``'/path/to/port'`` with the path to the port to which your Arduino is connected.

A `matplotlib figure`_ should appear and a real-time wave form should begin go to be drawn.
Calibration of the waveform within the figure make take up to 10 seconds.


Further Documentation
---------------------

Further documentation can be found on `Read the Docs`_.

.. _Read the Docs: http://olimex-ekg-emg.readthedocs.org/en/latest/

.. |docs| image:: https://readthedocs.org/projects/olimex-ekg-emg/badge/
    :alt: Documentation Status
    :scale: 100%
    :target: http://olimex-ekg-emg.readthedocs.org/en/latest/

.. _matplotlib figure: http://matplotlib.org/api/figure_api.html#figure

.. _Olimex EKG/EMG Shield: https://www.olimex.com/Products/Duino/Shields/SHIELD-EKG-EMG/