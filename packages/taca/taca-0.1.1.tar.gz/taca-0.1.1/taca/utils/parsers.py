""" Different file parsers for TACA
"""
import os
import xml.etree.ElementTree as ET


#######################################
# Raw data status/stats files parsers #
#######################################

def get_read_configuration(run_path):
    """Parse the RunInfo.xml to read configuration and return a list of dicts

    :param str run_path: Path to the run directory
    :returns: List of dicts corresponding to sections in RunInfo.xml
    :rtype: list
    :raises RunTimeError: If no RunInfo.xml file is found
    """
    reads = []
    run_info_file = os.path.join(run_path, "RunInfo.xml")
    try:
        tree = ET.ElementTree()
        tree.parse(run_info_file)
        read_elem = tree.find("Run/Reads")
        for read in read_elem:
            reads.append(dict(zip(read.keys(), [read.get(k) for k in read.keys()])))
        return reads
    except IOError:
        raise RuntimeError('No RunInfo.xml file found in {}. Please check.'.format(run_path))


def last_index_read(run):
    """Parse the number of the highest index read from the RunInfo.xml file

    :param str run: Run directory
    :returns: Highest index read
    :rtype: int
    """
    read_numbers = [int(read.get("Number", 0)) for read in get_read_configuration(run) if read.get("IsIndexedRead", "") == "Y"]
    return 0 if len(read_numbers) == 0 else max(read_numbers)
