==========================
Imspector Python Interface
==========================

Imspector comes with a Python Interface named SpecPy which can be used either 
from the embedded Python console or from an external Python console running on 
the same computer (to enable sharing of measurement data) or even running on a 
different computer. 

--------------------
Setup
--------------------

To setup SpecPy you first need to install

- Python 2.7.9 or 3.4.2 together with
- NumPy-MKL 1.8.2

Then from the Command Prompt run

.. code-block:: bat

  python.exe -m pip install specpy

--------------------
Start
--------------------

- Working from an external Python console you need to start the Imspector 
  Server

.. figure:: images/ImspectorRunServer.png

- To load the Python Interface just say

.. code-block:: python

  from specpy import *

--------------------
Interface
--------------------

Imspector
====================

.. code-block:: python

  Imspector()

first tries to return a local Imspector object (living in the same process) or 
else returns a proxy Imspector object connected to the Imspector Application 
running on `localhost`.

.. code-block:: python

  Imspector(host)

where :code:`host` is a host name returns a proxy Imspector object connected 
to the Imspector Application running on the corresponding host.

If :code:`imspector` is an Imspector object than

.. code-block:: python

  imspector.host()

returns the name of the host the Imspector Application is running on or an 
empty string in case the Imspector object is local (living in the same process),

.. code-block:: python

  imspector.version()

returns the current Imspector version,

.. code-block:: python

  imspector.device_drivers()

returns the Imspector device drivers as a dictionary of name value pairs,

.. code-block:: python

  imspector.parameter(path)

where :code:`path` is of the form `device/.../parameter_name` returns the 
corresponding Imspector parameter value,

.. code-block:: python

  imspector.set_parameter(path, value)

where :code:`path` is of the form `device/.../parameter_name` and :code:`value` 
is a value, sets the corresponding Imspector parameter value,

.. code-block:: python

  imspector.parameters()

returns the Imspector parameters as a dictionary of name value pairs,

.. code-block:: python

  imspector.set_parameters(dictionary)

where :code:`dictionary` is a dictionary of name value pairs sets the 
corresponding Imspector parameter values,

.. code-block:: python

  imspector.measurement_titles()

returns the list of titles of all open measurements in Imspector,

.. code-block:: python

  imspector.active_measurement()

for the currently active measurement in Imspector, returns the corresponding 
Measurement object,

.. code-block:: python

  imspector.measurement(title)

where :code:`title` is the title of an open measurement in Imspector, returns the 
corresponding Measurement object,

.. code-block:: python

  imspector.open(path)

where :code:`path` is the path to a measurement file, opens it in Imspector and 
returns the corresponding Measurement object,

.. code-block:: python

  imspector.activate(measurement)

where :code:`measurement` is a Measurement object, activates the corresponding 
measurement in Imspector,

.. code-block:: python

  imspector.start(measurement)

where :code:`measurement` is a Measurement object, starts the corresponding 
measurement in Imspector and returns immediately,

.. code-block:: python

  imspector.pause(measurement)

where :code:`measurement` is a Measurement object, pauses the corresponding 
measurement in Imspector,

.. code-block:: python

  imspector.stop(measurement)

where :code:`measurement` is a Measurement object, stops the corresponding 
measurement in Imspector,

.. code-block:: python

  imspector.run(measurement)

where :code:`measurement` is a Measurement object, runs the corresponding 
measurement in Imspector (starts it and returns when it has finished),

.. code-block:: python

  imspector.close(measurement)

where :code:`measurement` is a Measurement object, closes the corresponding 
measurement in Imspector,

.. code-block:: python

  imspector.connect_begin(callable, flag)

where :code:`callable` is a callable Python object, connects it to the 
corresponding begin signal in Imspector 
(if :code:`flag` is :code:`0` the begin of the whole measurement and 
if :code:`flag` if :code:`1` the begin of one measurement step),

.. code-block:: python

  imspector.disconnect_begin(callable, flag)

where :code:`callable` is a callable Python object, disconnects it from the 
corresponding begin signal in Imspector 
(if :code:`flag` is :code:`0` the begin of the whole measurement and 
if :code:`flag` if :code:`1` the begin of one measurement step),

.. code-block:: python

  imspector.connect_end(callable, flag)

where :code:`callable` is a callable Python object, connects it to the 
corresponding end signal in Imspector 
(if :code:`flag` is :code:`0` the end of the whole measurement and 
if :code:`flag` if :code:`1` the end of one measurement step),

.. code-block:: python

  imspector.disconnect_end(callable, flag)

where :code:`callable` is a callable Python object, disconnects it from the 
corresponding end signal in Imspector 
(if :code:`flag` is :code:`0` the end of the whole measurement and 
if :code:`flag` if :code:`1` the end of one measurement step).

Measurement
====================

If :code:`measurement` is a Measurement object than

.. code-block:: python

  measurement.title()

returns the title of the measurement,

.. code-block:: python

  measurement.number_of_configurations()

returns the number of configurations in the measurement,

.. code-block:: python

  measurement.configuration_titles()

returns the list of titles of all configurations in the measurement,

.. code-block:: python

  measurement.active_configuration()

for the currently active configuration in the measurement, returns the 
corresponding Configuration object,

.. code-block:: python

  measurement.configuration(index)

where :code:`index` is from the interval :math:`[0, number\_of\_configurations 
- 1]` in the measurement, returns the corresponding Configuration object,

.. code-block:: python

  measurement.configuration(title)

where :code:`title` is one of the configuration titles in the measurement, 
returns the corresponding Configuration object,

.. code-block:: python

  measurement.activate(configuration)

where :code:`configuration` is a Configuration object, activates the 
corresponding configuration in the measurement (if the measurement contains only one configuration, this configuration is activated by default),

.. code-block:: python

  measurement.parameter(path)

where :code:`path` is of the form `device/.../parameter_name`, returns the 
corresponding measurement parameter value for the currently active configuration,

.. code-block:: python

  measurement.set_parameter(path, value)

where :code:`path` is of the form `device/.../parameter_name` and :code:`value` 
is a value, sets the corresponding measurement parameter value for the currently active 
configuration,

.. code-block:: python

  measurement.parameters()

returns the measurement parameters for the currently active configuration as a 
dictionary of name value pairs,

.. code-block:: python

  measurement.set_parameters(dictionary)

where :code:`dictionary` is a dictionary of name value pairs, sets the 
corresponding measurement parameter values for the currently active configuration,

.. code-block:: python

  measurement.number_of_stacks()

returns the number of stacks in the measurement,

.. code-block:: python

  measurement.stack_titles()

returns the list of titles of all stacks in the measurement,

.. code-block:: python

  measurement.stack(index)

where :code:`index` is from the interval :math:`[0, number\_of\_stacks - 1]` 
in the measurement, returns the corresponding Stack object,

.. code-block:: python

  measurement.stack(title)

where :code:`title` is one of the stack titles in the measurement, returns 
the corresponding Stack object,

.. code-block:: python

  measurement.create_stack(type, sizes)

where :code:`type` is one of the `Data Types`_ and :code:`sizes` is a list of 
exactly four sizes of dimensions, creates a new stack and returns the 
corresponding Stack object,

.. code-block:: python

  measurement.update()

redraws all corresponding stacks in Imspector 
(useful when the stack content was changed from Python),

.. code-block:: python

  measurement.save_as(path[, compression])

where :code:`path` is a file path and :code:`compression` is :code:`True` by 
default or :code:`False` saves it into a file.

Configuration
====================

If :code:`configuration` is a Configuration object than

.. code-block:: python

  configuration.title()

returns the title of the configuration,

.. code-block:: python

  configuration.parameter(path)

where :code:`path` is of the form `device/.../parameter_name`, returns the 
corresponding measurement parameter value for this configuration,

.. code-block:: python

  configuration.set_parameter(path, value)

where :code:`path` is of the form `device/.../parameter_name` and :code:`value` 
is a value, sets the corresponding measurement parameter value for this 
configuration,

.. code-block:: python

  configuration.parameters()

returns the measurement parameters for this configuration as a dictionary of 
name value pairs,

.. code-block:: python

  configuration.set_parameters(dictionary)

where :code:`dictionary` is a dictionary of name value pairs, sets the 
corresponding measurement parameter values for this configuration,

.. code-block:: python

  configuration.number_of_stacks()

returns the number of stacks in this configuration,

.. code-block:: python

  configuration.stack_titles()

returns the list of titles of all stacks in this configuration,

.. code-block:: python

  configuration.stack(index)

where :code:`index` is from the interval :math:`[0, number\_of\_stacks - 1]` 
in this configuration, returns the corresponding Stack object,

.. code-block:: python

  configuration.stack(title)

where :code:`title` is one of the stack titles in this configuration, returns 
the corresponding Stack object.

File
====================

.. code-block:: python

  File(path, mode)

where :code:`path` is the path to an `.obf` or `.msr` file and :code:`mode` is 
either :code:`File.Read` or :code:`File.Write` or :code:`File.Append` opens it 
and returns the corresponding File object.

If :code:`file` is a File object than

.. code-block:: python

  file.description()

returns the description of the file,

.. code-block:: python

  file.set_description(description)

where :code:`description` is a string sets the description of the file,

.. code-block:: python

  file.number_of_stacks()

returns the number of stacks in the file,

.. code-block:: python

  file.read(position)

where :code:`position` is in the range from zero to the number of stacks, reads 
and returns the corresponding Stack object,

.. code-block:: python

  file.write(stack)

where :code:`stack` is a Stack object writes it to the file,

.. code-block:: python

  file.close()

closes it.

Stack
====================

.. code-block:: python

  Stack(type, sizes)

where :code:`type` is one of the `Data Types`_ and :code:`sizes` is a 
list of sizes of all dimensions, returns a new local Stack object.

If :code:`stack` is a Stack object than

.. code-block:: python

  stack.title()

returns the title of the stack,

.. code-block:: python

  stack.set_title(string)

where :code:`string` is a string sets the title. If another stack in the same measurement already has the same title, suffixes of the form [1], [2], .. are added.

.. code-block:: python

  stack.description()

returns the description,

.. code-block:: python

  stack.set_description(string)

where :code:`string` is a string, sets the description,

.. code-block:: python

  stack.number_of_elements()

returns the number of elements,

.. code-block:: python

  stack.number_of_dimensions()

returns the number of dimensions,

.. code-block:: python

  stack.size(dimension)

where :code:`dimension` is one of the dimensions returns the corresponding size
(the number of steps/positions in that dimension),

.. code-block:: python

  stack.sizes()

returns the list of sizes of all dimensions,

.. code-block:: python

  stack.label(dimension)

where :code:`dimension` is one of the dimensions returns the corresponding
label,

.. code-block:: python

  stack.set_label(dimension, string)

where :code:`dimension` is one of the dimensions and :code:`string` is a string 
sets the corresponding label,

.. code-block:: python

  stack.labels()

returns the list of labels of all dimensions,

.. code-block:: python

  stack.set_labels(strings)

where :code:`strings` is a list of strings for all dimensions sets the 
corresponding labels,

.. code-block:: python

  stack.length(dimension)

where :code:`dimension` is one of the dimensions returns the corresponding
length,

.. code-block:: python

  stack.set_length(dimension, number)

where :code:`dimension` is one of the dimensions and :code:`number` is a number 
sets the corresponding length,

.. code-block:: python

  stack.lengths()

returns the list of lengths of all dimensions,

.. code-block:: python

  stack.set_lengths(numbers)

where :code:`numbers` is a list of numbers for all dimensions sets the 
corresponding lengths,

.. code-block:: python

  stack.offset(dimension)

where :code:`dimension` is one of the dimensions returns the corresponding
offset,

.. code-block:: python

  stack.set_offset(dimension, number)

where :code:`dimension` is one of the dimensions and :code:`number` is a number 
sets the corresponding offset,

.. code-block:: python

  stack.offsets()

returns the list of offsets of all dimensions,

.. code-block:: python

  stack.set_offsets(numbers)

where :code:`numbers` is a list of numbers for all dimensions sets the 
corresponding offsets,

.. code-block:: python

  stack.data()

returns the data as a `NumPy array <http://docs.scipy.org/doc/numpy/reference/arrays.html>`_. Note that the shape of the array
is reversed regarding the order of the dimensions in Imspector and all other methods of Stack.

Data Types
====================

These are constants of the SpecPy module.

.. code-block:: python

  Int8
  UInt8
  Int16
  UInt16
  Int32
  UInt32
  Int64
  UInt64
  Float32
  Float64
  Complex64
  Complex128

--------------------
Examples
--------------------

Changes the exposure time of the sample camera.

.. code-block:: python

  from specpy import *
  imspector = Imspector()
  measurement = imspector.active_measurement()
  time = measurement.parameter('SimCam/ExposureTime')
  measurement.set_parameter('SimCam/ExposureTime', 2*time)

Opens a Stack and does some statistics.

.. code-block:: python

  from specpy import *
  imspector = Imspector()
  measurement = imspector.open(r"D:\Data\20120806_PD neurons Dioc.lif")
  import numpy
  threshold = 410
  # file = open('output.txt', 'w')
  for title in measurement.stack_titles() :
    stack = measurement.stack(title)
    data = stack.data()
    mean = data.mean()
    standard_deviation = data.std()
    print title, mean, standard_deviation
  #   print >> file, title, mean, standard_deviation
    masked_data = numpy.ma.masked_less(data, threshold)
    mean = masked_data.mean()
    standard_deviation = masked_data.std()
    print title, mean, standard_deviation
  #   print >> file, title, mean, standard_deviation
    numpy.putmask(data, data < threshold, 4095)

  # file.close()


