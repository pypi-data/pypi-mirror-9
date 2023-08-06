import os


def xml(xml_filename):
    """
    Returns xml_filename from xml/ directory as a string to the test.
    """
    file_path = os.path.abspath(
        os.path.join('eveapi2', 'tests', 'xml', '{}.xml'.format(xml_filename))
    )
    return open(file_path, 'r').read()
