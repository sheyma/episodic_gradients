from xml.etree import ElementTree as xmlt
import numpy as np
import sys

myfilename = sys.argv[1]
targetstri = sys.argv[2]
outfilenam = sys.argv[3]

def get_entry_target_coord(xml_fn, targetdesc):
    """Reads TMS Neuronavigator EntryTarget.xml file and returns coordinates
    for entry-target according to targetdesc.

    Expects exactly one result for Target and Entry.

    Params
    ------
    xml_fn: str
        Full file path to .xml file
    targetdesc: str
        Description of Target to get coordinates from.

    Returns
    -------
    dict
        'entry':  entry coordinates
        'target': target coordinates


    TMSNavigator does not seem to save descriptions for Entries, but only for
    Targets. This function assumes that the xml 'index=' parameter is the same
    for each entry-target pair. It reads the 'index=' value for the correct
    Target according to Description, and then reads coordinates for the Entry
    with that Index. The order of  the Entries and Targets in the .xml is
    not important.

    Example call:
    get_entry_target_coord("EntryTarget20170327113638528.xml", 'mPFC')
    
    Written by Ole Numssen. 

    """
    # load xml file as element tree
    entrytarget = xmlt.parse(xml_fn)

    # as I don't now how to work efficiently with ElementTree object, 
    #the following code is ugly but it's late...
    
    targets = entrytarget.findall('Target')
    entries = entrytarget.findall('Entry')

    # pull the 'index' variable from Target with correct Description
    target = [target for target in targets if target[0].attrib['description'] == targetdesc]
    assert len(target) == 1, "More or less than 1 target with descrption '{}' found".format(targetdesc)

    # now use this index to get the coordinates from the Entry with the Target.Index
    entry = [entry for entry in entries if entry.attrib['index'] == target[0].attrib['index']]
    assert len(entry ) == 1, "More or less than 1 entry with index '{}' found".format(target[0].attrib['index'])

    # get coordinates from Entry as np.ndarray
    entry_coordinates = np.array([entry[0][0][0].attrib['data0'],
                                  entry[0][0][0].attrib['data1'],
                                  entry[0][0][0].attrib['data2']]).astype(float)

    # get coordinates from Target as np.ndarray
    target_coordinates = np.array([target[0][0][0].attrib['data0'],
                                   target[0][0][0].attrib['data1'],
                                   target[0][0][0].attrib['data2']]).astype(float)

    return({'entry':entry_coordinates,
            'target':target_coordinates})

# go...
results = get_entry_target_coord(myfilename, targetstri)

myarray = np.array([results['target'], results['entry']])

np.savetxt(outfilenam , myarray,   delimiter='\t' ,  fmt='%2.2f')

