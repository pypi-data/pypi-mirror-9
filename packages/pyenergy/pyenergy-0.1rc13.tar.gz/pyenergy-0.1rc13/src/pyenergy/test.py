import pyenergy
import numpy

m1 = pyenergy.Measurement(1,2)
m2 = pyenergy.Measurement(3,4)

print m1
print m2

print numpy.mean([m1,m2])

print m1+m2
