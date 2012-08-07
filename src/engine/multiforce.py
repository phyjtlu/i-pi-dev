"""Contains the classes that deal with ring polymer contraction schemes.

Classes:
   MultiForce: Deals with ring polymer contraction schemes.
"""

__all__ = ['MultiForce']

import numpy as np
import math
from utils.depend import *
from engine.forces import *
from engine.beads import *

class MultiForce(dobject):
   """Deals with ring polymer contraction.

   Takes the positions of a ring polymer, and sends contracted ring polymer 
   positions to different driver codes.

   Attributes:
      natoms: An integer giving the number of atoms.
      nbeads: An integer giving the number of beads.
      _forces: A list of the forcefields which will be used to calculate
         the forces, potential and virial.
      _contracted: A list containing all the bead objects for each forcefield.
      Cb2nm: The transformation matrix between the bead and normal mode 
         representations.
      softexit: A function to help make sure the printed restart file is
         consistent.

   Depend objects:
      f: An array containing the components of the force.
      pots: A list containing the potential energy for each forcefield. 
      virs: A list containing the virial tensor for each forcefield. 
      pot: The total potential energy.
      vir: The virial tensor.
      fnm: An array containing the components of the force in the normal mode
         representation.
   """

   def __init__(self, forces = None, beads=None, cell=None):
      """Initialises Multiforce.

      Args:
         beads: Optional beads object, to be bound to the forcefield.
         cell: Optional cell object, to be bound to the forcefield.
         forces: Force field objects for each of the contracted ring polymers. 
      """

      if not (beads is None or cell is None or forces is None):
         self.bind(beads, cell, forces)

   def bind(self, beads, cell, forces, softexit=None):
      """Binds atoms, cell and forces to the forcefield.

      Args:
         bead: The Beads object from which the bead positions are taken.
         cell: The Cell object from which the system box is taken.
         forces: A list of the different forcefields for each of the contracted
            ring polymers. 
         softexit: A function to help make sure the printed restart file is
            consistent.
      """

      self.natoms = beads.natoms
      self.nbeads = beads.nbeads
      self.beads = beads
      self.softexit = softexit
      self._forces = [ForceBeads() for force in forces]

      self._contracted = []
      for f in range(forces):
         if forces[f].nreduced == 0:
            forces[f].nreduced = self.nbeads
         self._contracted.append(Beads(natoms=beads.natoms, 
            nbeads=forces[f].nreduced))
         dget(self._contracted[f], "q")._func = contract_wrapper(f)
         dget(self._contracted[f], "q").add_dependency(dget(self.beads,"qnm"))
         dget(self._contracted[f], "q").add_dependency(dget(self.beads,"q"))

      for f in range(len(forces)):
         self._forces[f].bind(self._contracted[f], cell, forces[f], softexit) 

      dset(self,"f",
         depend_array(name="f",value=np.zeros((self.nbeads,3*self.natoms)),
            func=self.f_gather,
               dependencies=[dget(force,"f") for force in self._forces]))

      dset(self,"pots",
         depend_array(name="pots",value=np.zeros((self.nbeads,3*self.natoms)),
            func=self.f_gather,
               dependencies=[dget(force,"pot") for force in self._forces]))

      dset(self,"virs",
         depend_array(name="virs",value=np.zeros((self.nbeads,3*self.natoms)),
            func=self.f_gather,
               dependencies=[dget(force,"vir") for force in self._forces]))

      dset(self,"pot",
         depend_value(name="pot", func=self.pot, 
            dependencies=[dget(self,"pots")]))
      dset(self,"vir",
         depend_value(name="vir", func=self.vir, 
            dependencies=[dget(self,"virs")]))

      dset(self,"fnm",
         depend_array(name="fnm",value=np.zeros((self.nbeads,3*self.natoms)),
            func=self.b2nm_f, dependencies=[dget(self,"f")]))
      self.Cb2nm = beads.Cb2nm
      self.Cnm2b = beads.Cnm2b

   def queue(self):
      """Submits all the required force calculations to the interface."""

      for force in self._forces:
         force.queue()

   def b2nm_f(self):
      """Transforms force array to normal mode representation.

      Returns:
         An array giving all the force components in the normal mode
         representation. Normal mode i is given by fnm[i,:].
      """

      return np.dot(self.Cb2nm,depstrip(self.f))

   def pot_gather(self):
      """Obtains the potential energy for each replica.

      Returns:
         A list of the potential energy of each replica of the system.
      """

      self.queue()
      return np.array([f.pot for f in self._forces])

   def vir_gather(self):
      """Obtains the virial for each replica.

      Returns:
         A list of the virial of each replica of the system.
      """

      self.queue()
      (f, vir) = self.expand()
      return vir

   def f_gather(self):
      """Obtains the global force vector.

      First transforms the bead coordinates to the appropriate contracted
      ring polymer, then calculates the forces on each.

      Returns:
         An array with all the components of the force for each of the
         contracted ring polymers.
      """

      self.queue()
      (f, vir) = self.expand()
      return f

   def pot(self):
      """Sums the potentials acting on each of the contracted ring polymers."""

      return self.pots.sum() 

   def vir(self):
      """Sums the virial of each of the contracted ring polymers. 

      Not the actual system virial.
      """

      vir = np.zeros((3,3))
      for v in self.virs:
         vir += v
      return vir

   def contract(self, i=0):
      """Computes the contracted ring polymers."""

      nred = self._forces[i].nreduced
      newq = numpy.zeros(nred)
      if nred == self.nbeads:
         newq = self.beads.q
      else:
         for j in range(-nred/2+1, nred/2+1):
            newq = np.dot(self._contracted[i].Cnm2b[:,j], depstrip(self.beads.qnm))*math.sqrt(nred/float(self.nbeads))

      return newq

   def contract_lambda(self, i=0):
      """Wrapper for the function contract()."""

      return lambda: contract(i)

   def expand(self):
      """Transforms the force acting on each of the contracted ring polymers
      back to the full ring polymer.

      Returns:
         The total force over each of the forcefields.
      """

#TODO make this the _func for self.f and self.vir
      newf = np.zeros((self.nbeads,3*self.natoms))
      vir = np.zeros((3,3))

      for i in range(len(self._forces)):
         nred = self.nreduced[i]
         if nred == self.nbeads:
            newf += self._forces[i]
         else:
            for j in range(-nred/2+1,nred/2+1):
               newf[j] += np.dot(self.Cnm2b[:,j],depstrip(self._forces[i].fnm))*math.sqrt(self.nbeads/float(nred))

      #TODO do the same for the virial.
      # I think we need: W = T.T*W_contracted*(T.T)^(-1) = T.T*W_contracted*T

      #TODO do this with FFT

      return newf
