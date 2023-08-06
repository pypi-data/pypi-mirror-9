""" Test utilities
"""
import os
from StringIO import StringIO

def loadfile(rel_filename):
    """ Open a file relative to this module
    """
    storage_path = os.path.join(os.path.dirname(__file__))
    file_path = os.path.join(storage_path, rel_filename)
    file_ob = open(file_path, 'rb')
    filedata = file_ob.read()
    filename = file_path.split('/')[-1]
    filename = str(filename)
    return {
        'name': filename,
        'data': filedata,
    }

def preparefile(rel_filename, ctype='application/pdf'):
    """ Prepare a file for upload
    """
    ofile = loadfile(rel_filename)
    fp = StringIO(ofile.get('data'))
    fp.filename = ofile.get('name')
    return fp

def loadblobfile(context, rel_filename, ctype='application/pdf'):
    """ load a file
    """
    context.setFile(preparefile(rel_filename, ctype))
    return 'File uploaded.'
