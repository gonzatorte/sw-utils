import StringIO
from sw_utils.std_capture import get_capture, configure, get_capture_mng

configure()

c = get_capture()

s1 = (StringIO.StringIO(), StringIO.StringIO())
s2 = (StringIO.StringIO(), StringIO.StringIO())

print "Se ve"
with (get_capture_mng(*s1)):
    print "cap 1"
    with (get_capture_mng(*s2)):
        print "cap 2"
    #Escribir en stderr...
print "Se vuelve a ver"


s1[0].seek(0)
s1[1].seek(0)
s1o = s1[0].read()
s1e = s1[1].read()

s2[0].seek(0)
s2[1].seek(0)
s2o = s2[0].read()
s2e = s2[1].read()

print s1o
print s2o
