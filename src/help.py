"""Help script which automatically generates help files.

A full help message can be found by running 'python help.py -h' or
'python help.py --help'.

Functions:
   help: Writes the help file.
"""

import sys
from inputs import *
from utils.io.io_xml import *
from optparse import OptionParser

__all__ = ['help']

objects = {'barostats': barostats.InputBaro(), 'cell': cell.InputCell(), 'simulation': simulation.InputSimulation(), 'ensembles': ensembles.InputEnsemble(), 'thermostats': thermostats.InputThermo(), 'interface': interface.InputInterface(), 'forces': forces.InputForce(), 'atoms': atoms.InputAtoms(), 'beads': beads.InputBeads(), 'prng': prng.InputRandom()}

usage = "usage: python %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-x", action="store_true", dest = "xml", default=False, help="write an xml help file")
parser.add_option("-l", action="store_true", dest = "latex", default=False, help="write a latex help file")
parser.add_option("-n", action="store", type="int", dest="levels", help="number of levels depth to which data is printed out")
parser.add_option("-o", action="store", dest="prefix", help="Prefix for the output files", default="help")
parser.add_option("-i", action="store", dest="opt", help="Root object for the help files. Options: ['barostats', 'cell', 'simulation', 'ensembles', 'thermostats', 'interface', 'forces', 'atoms', 'beads', 'prng']", default='simulation')
parser.add_option("-r", action="store_true", dest = "ref", default=False, help="add references to a latex help file. Ignored if -l is not present")
(options, args) = parser.parse_args()

if options.opt not in objects:
   raise ValueError("Option " + options.opt + " is not a viable tag name")

def help(latex=False, xml=False, levels = None, option='simulation', prefix="help", ref=False):
   """Writes the help file.

   Will write an xml file 'prefix.xml' if xml=True and a latex file 'prefix.tex'
   if latex=True. Will write out tags to a depth equal to the value of levels, 
   if it is specified, and will print using a root tag as specified by 
   the value of option.

   Args:
      latex: Boolean specifying whether a latex file will be printed.
      xml: Boolean specifying whether an xml file will be printed.
      levels: An integer specifying how many layers of the hierarchy will be 
         printed. If not given, all layers will be printed.
      option: A string specifying which object will be used as the root object
         for the latex and xml files. Defaults to 'simulation'.
      prefix: File prefix for the output files. Defaults to 'help'.
   """

   simrestart = objects[option]
   
   if xml:
      xml_output = open(prefix + ".xml","w")
      xml_output.write(simrestart.help_xml(name=option, stop_level=levels))
   if latex:
      latex_output = open(prefix + ".tex","w")
      latex_output.write(simrestart.help_latex(stop_level=levels, ref=ref))

if __name__ == '__main__':
   help(options.latex, options.xml, options.levels, options.opt, options.prefix, options.ref)
