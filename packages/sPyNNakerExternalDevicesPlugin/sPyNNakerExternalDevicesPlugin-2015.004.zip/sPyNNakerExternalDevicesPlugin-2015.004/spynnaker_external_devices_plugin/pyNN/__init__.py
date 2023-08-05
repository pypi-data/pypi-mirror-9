"""
The :py:mod:`spynnaker.pynn` package contains the frontend specifications
and implementation for the PyNN High-level API
(http://neuralensemble.org/trac/PyNN)
"""

#external models
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_cochlea_device import ExternalCochleaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_fpga_retina_device import ExternalFPGARetinaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_motor_device import MunichMotorDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_retina_device import MunichRetinaDevice
from spynnaker_external_devices_plugin.pyNN.control_models.\
    munich_motor_control import MunichMotorControl
from spynnaker_external_devices_plugin.pyNN.control_models.reverse_ip_tag_multi_cast_source \
    import ReverseIpTagMultiCastSource

from spinnman.messages.eieio.eieio_prefix_type import EIEIOPrefixType