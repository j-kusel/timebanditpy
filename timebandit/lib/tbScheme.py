from tbLib import InstManager, Measure, Rhythm
import tbImg

class Scheme(object):
    def __init__(self):
        self.inst = InstManager()

    def create_inst(self, name='default'):
        """add a new instrument"""
        self.inst[str(name)] = []
    
    def del_inst(self, name=''):
        """remove an instrument"""
        try:
            del self.inst[str(name)]
        except IndexError:
            break

    def create(self, instrument='', start='', end='', time=''):
        """add measure to database from current input data"""
        measure_data = [instrument, start, end, time]
        if '' not in measure_data:
            self.inst[self.inst.index(measure_data[0])] += Measure(*measure_data)

    def generate_image(self, opacity=50, divisions=4):
        """plot image"""
        tbImg.reset()
        o = int(float(self.imgpop.opslider.get())/100*255)
        tbImg.setopacity(int(opacity/100*255))
        tbImg.setbpi(int(divisions))
        for i in self.inst:
            tbImg.addinst(self.inst[i])
        tbImg.plot()
        #self.imgpop.destroy()

