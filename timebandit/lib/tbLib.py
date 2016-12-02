from collections import OrderedDict
from ConcatList import ConcatList
from scipy import integrate

class InstManager(OrderedDict):
    """
    ordered dictionary for measure storage in ConcatList
    """
    def __init__(self, name='<<null>>'):
        super(InstManager, self).__init__()

    def __missing__(self, key):
        """
        initialize a key as a ConcatList no matter what
        """
        self[key] = ConcatList()
        return self[key]

    def __setitem__(self, key, value):
        """
        ensures that measures are put into a ConcatList
        """
        if not isinstance(value, ConcatList):
            value = ConcatList(value)
        return super(InstManager, self).__setitem__(key, value)

    def __str__(self):
        """
        print the InstManager as a series of keys and their Measures
        """
        strm = []
        for i in self:
            strm.append('Instrument: {}'.format(i))
            for m in self[i]:
                strm.append('\t{}: {}'.format(m.__class__.__name__, m))
        return '/n'.join(strm)

    def index(self, i):
        """
        takes an index and returns a key for retrieval
        """
        return self.keys()[i]

    #def add_measure(self, inst, meas):
    #    self[inst] += meas

class Measure:
    """
    timebandit Measure class to handle storage/location/time computation
    """

    def __init__(self, whichinst, begin, end, timesig, offset=0):
        self.begin = begin
        self.end = end
        self.timesig = timesig
        self.offset = offset
        self.beats = []
        self.Calc()
        self.beatstr = self.Beat_disp()

    def __str__(self):
        return '{0} to {1}; {2} beats, {3}ms'.format( \
            self.begin, self.end, self.timesig, self.beats[-1])

    def Shift(self, pivot, beat): #started reworking how offset works
        """change measure offset"""
        self.offset = pivot - beat
        self.beatstr = self.Beat_disp()

    def Calc(self):
        """recalculates equation and beat times"""
        self.eq = lambda x: \
            (60000/((self.end-self.begin)/self.timesig*x+self.begin))
        self.beats = [int(integrate.quad(self.eq,0,b)[0]) \
                      for b in range(0,int(self.timesig+1))]

    def Beat_disp(self):
        """returns beat info as string"""
        return ' '.join([str(x+self.offset) for x in self.beats])

    def Eval(self, beat, start=0):
        return int(integrate.quad(self.eq,start,beat)[0])

class Rhythm:

    def __init__(self, parent): #initialize with tie to Measure
        self.peq = parent.eq
        self.transients = []

    def Add_tr(self, note):
        self.transients.append(int(integrate.quad(self.peq,0,note)))
        self.Update_tr()

    def Del_tr(self, which):
        pass

    def Update_tr(self):
        pass

def __test__():
    inst = InstManager()
    for i in range(0,3):
        inst[i] = Measure(i, 60,120,5)
        inst[i] += Measure(i, 72,144,6)
        inst[i] += Measure(i, 96,152,7)
    print [i for i in inst]

if __name__ == "__main__":
    __test__()
