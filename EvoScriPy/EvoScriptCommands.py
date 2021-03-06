# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2016

__author__ = 'qPCR4vir'

import EvoScriPy.EvoMode
import EvoScriPy.Labware
from EvoScriPy.Instruction_Base import *
from EvoScriPy.Instructions import *


def Aspirate( tipMask,
              liquidClass,
              volume,
              grid,
              site,
              spacing,
              wellSelection,       # todo implement how to use alternative well selection?
              noOfLoopOptions,
              #loopName,
              #action,
              #difference,
              arm,
              RackName=None,
              Well=None):
    """
    :param difference:
    :param action:
    :param loopName:
    :param site:
    :param spacing:
    :param wellSelection:
    :param noOfLoopOptions:
    :param tipMask: int 0 - 255, selected tips, bit-coded (tip1 = 1, tip8 = 128)
    :param liquidClass: str,
    :param volume: expr[12], 12 expressions which the volume for each tip. 0 for tips which are not used or not fitted.
    :param grid: int, 1 - 67, labware location - carrier grid position
    :param RackName:
    :param Well:
    """
    a = aspirate( RackName , Well)
    a.tipMask       = tipMask
    a.liquidClass   = liquidClass
    a.volume        = volume
    a.labware.location = EvoScriPy.Labware.Labware.Location(grid,site)

    return a, a.exec()

def Dispense(tipMask,liquidClass,volume,grid, site, spacing, wellSelection,      # todo implement currectly. how to use alternative well selection?
             LoopOptions,
             arm):
    """
    :param tipMask: int 0 - 255, selected tips, bit-coded (tip1 = 1, tip8 = 128)
    :param liquidClass: str,
    :param volume: expr[12], 12 expressions which the volume for each tip. 0 for tips which are not used or not fitted.
    :param grid: int, 1 - 67, labware location - carrier grid position
    :param RackName:
    :param Well:
    """
    a = dispense( arm=arm)
    a.tipMask       = tipMask
    a.liquidClass   = liquidClass
    a.volume        = volume
    a.labware.location = EvoScriPy.Labware.Labware.Location(grid,site)
    a.loopOptions=LoopOptions

    return a, a.exec()


