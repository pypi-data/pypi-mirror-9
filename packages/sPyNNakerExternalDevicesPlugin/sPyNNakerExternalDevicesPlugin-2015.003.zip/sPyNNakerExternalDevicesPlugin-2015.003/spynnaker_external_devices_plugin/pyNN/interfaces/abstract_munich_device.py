#inhittance imports
from abc import ABCMeta

from six import add_metaclass

from spynnaker_external_devices_plugin.pyNN.links.abstract_spinn_link_device import AbstractSpinnLinkDevice


@add_metaclass(ABCMeta)
class AbstractMunichDevice(AbstractSpinnLinkDevice):
    def __init__(self, n_neurons, virtual_chip_coords, connected_node_coords,
                 connected_node_edge, machine_time_step, label,
                 max_atoms_per_core):
        AbstractSpinnLinkDevice.__init__(
            self, n_neurons, virtual_chip_coords, connected_node_coords,
            connected_node_edge, machine_time_step, label, max_atoms_per_core)

    @property
    def model_name(self):
        return "ExternalDeviceWithMunichInterface:{}".format(self.label)
