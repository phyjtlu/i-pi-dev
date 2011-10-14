from numpy import *
from engine import *
import sys
from engine import test_Thermo
from engine import io_system
from engine import dynamics
from engine import forces

print "hello world"

nat = 3
allthing = zeros((nat,6), float)

f = open("./testfile.txt","r")
syst=engine.System.from_pdbfile(f)
print syst

#syst.step(1.0)
#print syst
#syst.apply_pbc()
#print syst
#io_system.print_pdb(syst.atoms, syst.cell)

#print syst.kinetic()

#################################

x=allthing[0,0:3]
p=allthing[0,3:6]

print allthing

x[0]=1
p[2]=2
print allthing

x11=allthing[1,1]
x11=4
print allthing

x11=allthing[1:2,1]
x11[0]=4
print allthing

print
print "first cell = ", syst.cell
a, b, c, alpha, beta, gamma = cell.h2abc(syst.cell.h)

print "cell in new coordinates: ", a, b, c, alpha, beta, gamma
syst.cell.h=cell.abc2h(a, b, c, alpha, beta, gamma)

print "back to the start?", syst.cell
print

io_system.print_pdb(syst.atoms,syst.cell)

f.close()
f = open("./testfile.txt", "r")

alist,cell, natoms = io_system.read_pdb(f)

print alist
print cell
print "natoms = ", natoms

myih=syst.cell.ih
myih=syst.cell.ih
myih=syst.cell.ih

print "Trying to call the setter"
print syst.cell.h
print syst.cell.pot()
print syst.cell.pot()

hh = 2*identity(3, float)
syst.cell.h = hh
print syst.cell.pot()
hh[0,1] = -0.2
hh[0,2] = 0.7
hh[1,2] = 1.5
syst.cell.h = hh
print syst.cell.pot()
print "Setter called?"
myih=syst.cell.ih


print syst.cell.h

print syst.atoms[0]
print syst.atoms[1]
print syst.cell.minimum_distance(syst.atoms[0], syst.atoms[1])


print  "before", syst.atoms[0]
print syst.cell
syst.atoms[0] = syst.cell.apply_pbc(syst.atoms[0])
print "after", syst.atoms[0]

lang=langevin.Thermo_Langevin()
lang.dt=4
print lang.dt

print lang.temp

test = test_Thermo.Thermo_test()
test.dt = 4
print test.dt

print test.temp
print

f.close()
f = open("./testfile.txt", "r")

#thermo = langevin.Thermo_Langevin(dt = 0.1)
thermo = langevin.Thermo_Langevin
pot_func = forces.LJ
kwargs = {"eps": 0.1, "sigma": 0.15, "rc": 0.15*2.5}
syst2 = dynamics.NST_ens.from_pdbfile(f, thermo, pot_func, dt = 0.0001, **kwargs)

print syst2.syst
print syst2.thermo.dt
print syst2.thermo.temp

print 
print "SIMULATION STARTS HERE!"

syst2.simulation(10000)

#syst3 = dynamics.NST_ens.from_ensemble(syst2)
#syst3 = engine.System.from_system(syst2.syst)
#print
#print "syst2: ", syst2.syst
#print "syst3: ", syst3.syst

#print
#print syst2.syst.cell.p*syst2.dt/syst2.syst.cell.w
#print syst2.exp_p()
#print

print "goodbye world"
#print sys.atoms[3].pos.x, sys2.atoms[3].pos.x


