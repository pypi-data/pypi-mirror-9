import os
import re

#import numpy
#import seabird
from seabird.cnv import fCNV
#from seabird import CNVError
#from seabird.cnv import fCNV

from pydap.model import *
from pydap.handlers.lib import BaseHandler
from pydap.handlers.helper import constrain

class Handler(BaseHandler):

    extensions = re.compile(r'^.*\.cnv$', re.IGNORECASE)

    def __init__(self, filepath):
        self.filepath = filepath
        #self.filename = os.path.split(filepath)[1]
        #self.f = numpy.load(filepath)

    def parse_constraints(self, environ):
        try:
            f = fCNV(self.filepath)
        except:
            message = 'Unable to open file %s.' % self.filepath
            print self.filepath
            raise OpenFileError(message)

        # ====
        #s = StructureType(name='s')
        dataset = SequenceType(name=f.attributes['filename'],
                attributes=f.attributes)
        for k in f.keys():
            dataset[k] = BaseType(name=k, data=f[k], shape=f[k].shape,
                    type=f[k].dtype.char) #, attributes=f.attributes)
        # ====

        return constrain(dataset, environ.get('QUERY_STRING', ''))

if __name__ == '__main__':
    import sys
    from paste.httpserver import serve

    application = Handler(sys.argv[1])
    serve(application, port=8001)
