=============================================
os_virtual_interfacesv2_python_novaclient_ext
=============================================

Adds virtual interface extension support to python-novaclient.

This extension is autodiscovered once installed. To use::

    pip install os_virtual_interfacesv2_ext
    nova virtual-interface-create    Add a new virtual interface to an instance
    nova virtual-interface-delete    Removes the specified virtual interface from
                                     an instance
    nova virtual-interface-list      Lists the virtual interfaces for an instance
