from obitools import utils
from obitools import NucSequence
from obitools.utils import universalOpen, universalTell, fileSize, progressBar
import struct
import sys


class EcoPCRFile(utils.ColumnFile):
    def __init__(self,stream):
        utils.ColumnFile.__init__(self,
                                  stream, ' | ', True, 
                                  (str,int,int,
                                   str,int,str,
                                   int,str,int,
                                   str,int,str,
                                   str,str,int,float,
                                   str,int,float,
                                   int,
                                   str,str), "#")


    def next(self):
        data = utils.ColumnFile.next(self)
        seq = NucSequence(data[0],data[20],data[21])
        seq['seq_length_ori']=data[1]
        seq['taxid']=data[2]
        seq['rank']=data[3]
        seq['species']=data[4]
        seq['species_name']=data[5]
        seq['genus']=data[6]
        seq['genus_name']=data[7]
        seq['family']=data[8]
        seq['family_name']=data[9]
        seq['strand']=data[12]
        seq['forward_match']=data[13]
        seq['forward_error']=data[14]
        seq['forward_tm']=data[15]
        seq['reverse_match']=data[16]
        seq['reverse_error']=data[17]
        seq['reverse_tm']=data[18]
                 
        return seq
    
        
        
class EcoPCRDBFile(object):
    
    def _ecoRecordIterator(self,file,noError=False):
        file = universalOpen(file,noError)
        (recordCount,) = struct.unpack('> I',file.read(4))
        self._recover=False
    
        if recordCount:
            for i in xrange(recordCount):
                (recordSize,)=struct.unpack('>I',file.read(4))
                record = file.read(recordSize)
                yield record
        else:
            print >> sys.stderr,"\n\n  WARNING : EcoPCRDB reading set into recover data mode\n"
            self._recover=True
            ok=True
            while(ok):
                try:
                    (recordSize,)=struct.unpack('>I',file.read(4))
                    record = file.read(recordSize)
                    yield record
                except:
                    ok=False
                