__author__ = 'Ariel'

import EvoMode
import Labware

class EvoTypes: # TODO improve EvoTypes: string1: "V[~i~]", string2: V[~i~], integer, float, expr[12]
    def __init__(self, data):
        self.data = data
    #def __eq__(self, other):

    def __str__(self): # todo implement exceptions
        return str(self.data)

class string1(EvoTypes):
    #def __init__(self, data):
    #   EvoTypes.__init__(self,data)

    def __str__(self):
        return '"'+ str(self.data) + '"'

class expression(string1):
    pass

class expr(EvoTypes):
    def __init__(self, dim, data):
        self.dim = dim
        self.data = data

    def split(self):  #TODO 0 instant "0" ???? ; split - is not an elegant solution
        if isinstance(self.data,list):
            d=self.dim-len(self.data)
            assert (d>=0)
            return [expression(v) for v in self.data+[0]*d]
        else:
            return [expression(self.data)]*self.dim

class string2(EvoTypes):
    pass


class integer(EvoTypes):
    pass

class floating_point(EvoTypes):
    pass


class LoopOption:
    def __init__(self, name, action, difference):
        self.name=name
        self.action=action
        self.difference=difference

    VaryColumn=0
    VaryRow=1
    VaryWell=2
    VaryRack=3

class Instruction:
    def __init__(self, name):
        self.name = name
        self.arg = []

    def validateArg(self):
        return False

    def exec(self, mode=EvoMode.CurEvo):
        mode.exec(self)

    def __str__(self):
        self.validateArg()
        return self.name + "(" + ','.join([          ''   if    a is None
                                           else '"'+a+'"' if isinstance(a,str)
                                           else  str(a)       for a in self.arg]) + ")"

def_TipMask=15
curTipMask = def_TipMask
def_liquidClass="Water free DITi 1000"
def_vol=[0]*12
def_LabW = Labware.Labware(type=Labware.MP96well)
def_LoopOp = []
def_WashWaste = Labware.WashWaste
def_WashCleaner = Labware.WashCleanerS
def_DiTiWaste = Labware.DiTiWaste
def_AirgapSpeed= 300

class Pippet(Instruction):
    LiHa1 = 0
    LiHa2 = 1
    def __init__(self, name, tipMask     = curTipMask,
                             labware     = def_LabW,
                             spacing     = 1,
                             wellSelection = None,
                             LoopOptions = def_LoopOp,
                             RackName    = None,
                             Well        = None,
                             arm         = LiHa1):
        Instruction.__init__(self, name)
        self.tipMask=tipMask
        self.labware=labware
        self.spacing = spacing
        self.loopOptions = LoopOptions
        self.RackName = RackName
        self.Well = Well
        self.arm = arm
                            # noOfLoopOptions,
                            # loopName,
                            # action,
                            # difference,

    def validateArg(self):
        self.arg  =  [integer(self.tipMask)]                                                    # arg 1
        self.arg +=  [integer(self.labware.location.grid), integer(self.labware.location.site), # arg 2, 3
                      integer(self.spacing),         string1( self.labware.wellSelectionStr()) ]# arg 4, 5
        self.arg +=  [integer(len(self.loopOptions))]                                           # arg 6
        for op in self.loopOptions:
            self.arg +=  [string1(op.name), integer(op.action), integer(op.difference) ]        # arg 7, 8, 9
        self.arg +=  [integer(self.arm)]                                                        # arg 10

        return True


class Pippeting(Pippet):
    def __init__(self, name, tipMask     = curTipMask,
                             liquidClass = def_liquidClass,
                             volume      = def_vol,
                             labware     = def_LabW,
                             spacing     = 1,
                             wellSelection= None,
                             LoopOptions = def_LoopOp,
                             RackName    = None,
                             Well        = None,
                             arm         = Pippet.LiHa1):
        Pippet.__init__(self, name, tipMask    ,
                             labware     ,
                             spacing    ,
                             wellSelection,
                             LoopOptions,
                             RackName    ,
                             Well      ,
                             arm       )
        self.liquidClass=liquidClass
        self.volume=volume

    def validateArg(self):
        Pippet.validateArg(self)

        self.arg[1:1] = [string1(self.liquidClass)] + expr(12,self.volume).split()          # arg 2, 3 - 14
        return True


class DITIs(Instruction):
    def __init__(self, name, tipMask= curTipMask,  options=0, arm= Pippet.LiHa1):
        """

        :param name: str, instruction
        :param tipMask:
        :param options: int, 0-1. bit-coded 1 = if diti not fetched try 3 times then go to next position
        :param arm:
        """
        Instruction.__init__(self, name )
        self.options = options
        self.tipMask=tipMask
        self.arm = arm

    def validateArg(self):
        Instruction.validateArg(self)
        self.arg  =  [integer(self.tipMask)]                                                    # arg 1
        self.arg += [integer(self.options)]
        self.arg +=  [integer(self.arm)]                                                        # arg 10
        return True
