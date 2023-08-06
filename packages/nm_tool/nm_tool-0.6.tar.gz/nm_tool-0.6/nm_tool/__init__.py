#!/usr/bin/env python

import commands
import re

__all__ = ['parse', 'get_dict']


def parse(output):
    """Parses the complete output of nm-tool, and returns a dictionary with
    the results. The properties of each interface will appear in the dict
    under the interface name. Global properties will appear under a '_' key.
    """
    # global properties will show up under _
    interfaces = {'_': {}}
    interface = '_'
    lines = output.splitlines()
    in_scan_results = False
    for line in lines:
        line = line.strip()
        if line.startswith('-'):
            line = line.strip('-').strip()
            interface = line.split(':')[1].strip()
            name = None
            if '[' in interface:
                interface_plus_name = interface.split('[')
                interface = interface_plus_name[0].strip()
                name = interface_plus_name[1].rstrip(']').strip()
            interfaces[interface] = {'name': name}
        elif 'Wireless Access Points' in line:
            interfaces[interface]['scan_results'] = {}
            in_scan_results = True
        elif ':' in line:
            # this is a property of the interface
            try:
                if in_scan_results:
                    key, value = line.split(':', 1)
                    value = value.strip()
                    key = key.lstrip('*')
                    interfaces[interface]['scan_results'][key] = value
                else:
                    line = re.sub("(.*?)( )(.*:)", "\g<1>_\g<3>", line)
                    key, value = line.split(None, 1)
                    key = key.rstrip(':')
                    key = key.lower()
                    interfaces[interface][key] = value
            except ValueError:
                # ignore lines which aren't properties
                pass
        else:
            # this is a break between sections
            in_scan_results = False
    return interfaces


def get_dict():
    """Runs 'nm-tool' and then parses its output. Returns the result dict
    from 'parse()' if successful, otherwise returns None."""
    status, output = commands.getstatusoutput("nm-tool")
    if status == 0:
        return parse(output)
    return None
