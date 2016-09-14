from scipy import integrate

def Calc(self, a, b, size):
    """returns collection of beat times when given start/end/length"""
    eq = lambda x: (60000/((b-a)/size*x+a))
    points = []
    points.append(0)
    for j in range(1, int(size)):
        points.append(integrate.quad(eq,0,j)[0])
    return points

def tempo_test(mstr, slv, whichend):
    tries = 100
    tolerance = 10

    eq_m = lambda x: (60000/((mstr[1]-mstr[0])/mstr[2]*x+mstr[0]))

    f_m = integrate.quad(eq_m,0,mstr[2]-1)[0]
    for i in range(0, tries):
        eq_s = lambda x: (60000/((slv[1]-slv[0])/slv[2]*x+slv[0]))
        f_s = integrate.quad(eq_s,0,slv[2]-1)[0]
        dist = f_m - f_s
        if whichend=='start':
            response = slv[1]
        else:
            response = slv[0]
        print "at try %d we are %d away. end=%f" % (i, dist, response)
        if (abs(dist)<=tolerance):
            print "success! new end: %f" % (slv[1])
            break
        if dist > 0:
            if whichend=='start':
                slv[1]-=1
            else:
                slv[0]-=1
        else:
            if whichend=='start':
                slv[1]+=1
            else:
                slv[0]+=1
    print "end tempo: %f" % (slv[1])

def timesig_test(mstr, slv):
    tries = 100
    tolerance = 10

    eq_m = lambda x: (60000/((mstr[1]-mstr[0])/mstr[2]*x+mstr[0]))
    f_m = integrate.quad(eq_m,0,mstr[2]-1)[0]
    eq_s = lambda x: (60000/((slv[1]-slv[0])/slv[2]*x+slv[0]))
    f_s = integrate.quad(eq_s,0,slv[2]-1)[0]
    print f_m, f_s

    for i in range(0, tries):
        eq_s = lambda x: (60000/((slv[1]-slv[0])/slv[2]*x+slv[0]))
        f_s = integrate.quad(eq_s,0,slv[2]-1)[0]
        dist = f_m - f_s
        if abs(dist)<=tolerance:
            print "success! new timesig: %f, %d away" % (slv[2],dist)
            break
        if dist>0:
            slv[2]+=.25
        else:
            slv[2]-=.25
        print "at try %d we are %d away" % (i, dist)
        
test1 = [252, 144.0, 11]
test2 = [144, 54.0, 7]

tempo_test(test1, test2, 'end')
timesig_test(test2, test1)
