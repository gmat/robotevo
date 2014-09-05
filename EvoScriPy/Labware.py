__author__ = 'qPCR4vir'

import EvoMode


class WorkTable: # todo Implement !, parse WT from export file, template and scripts *.txt, *.ewt, *.est, *.esc
    """ Collection of Racks.Types and Labware.Types and pos of instances """

    def __init__(self,templateFile=None):
        self.labTypes= {}  # typeName,type. The type mountain a list of labware (with locations)
        self.Racks = []
        self.nGrid = 67   # max
        self.grid=[None]*67
        if isinstance(templateFile,list):
            self.template = templateFile
        else:
            self.template = self.parseWorTableFile(templateFile)

    def parseWorTableFile(self, templateFile):
        if not templateFile: return []
        templList=[]
        with open(templateFile) as tmpl:
            for line in tmpl:            #todo do the real complete parse
                templList += [line]
                if line.startswith("--{ RPG }--"): break
        return templList

    def addLabware(self, labware ):

        if labware.location.grid >= self.nGrid:
            raise "This WT have only " + self.nGrid + " grid."

        if  labware.type.name not in self.labTypes :
            self.labTypes[labware.type.name]=[]
        self.labTypes[labware.type.name] += [labware]


curWorkTable = WorkTable()

class Rack:
    """ Collection of Labwares sites, filled with labwares... """
    class Type:
        def __init__(self,name, width = 1, nSite = 1):
            self.width = width
            self.nSite = nSite
            self.allowedLabwaresTypes = []
            self.name = name

    def __init__(self, RackType, grid, label="", worktable=curWorkTable):
        self.site = grid
        self.type = RackType
        self.labwares = [None] * self.nSite
        self.label = label

    def addLabware(self, labware, site):
        if labware.type.name not in self.allowedLabwaresTypes:
            raise "Labware not allowed"

        if site >= self.Type.nSite:
            raise "This rack " + self.Type.name + ":" + self.label + " have only " + self.Type.nSite + " sites."

        if self.labwares[site] is not None:
            print ("Warning: you replaced an existed labware")

        self.labwares[site] = labware
        if labware.location.grid !=self.grid:
            if labware.location.grid is not None:
                print ("Warning, original grid changed to that of the Rack.")
            labware.location.grid=self.grid



class Well:
    def __init__(self, labware, Well_Offset):
        assert isinstance(Well_Offset, int)
        self.offset = Well_Offset
        self.vol = 0
        self.selFlag = False
        self.reactive = None
        self.label   = ""


class Labware:
    class Type:
        def __init__(self, name, nRow, nCol=1, maxVol = None, conectedWells=False):
            self.conectedWells = conectedWells
            self.name = name
            self.nRow = nRow
            self.nCol = nCol
            self.maxVol = maxVol

    class Location:
        def __init__(self, grid=None, site=None, rack=None, rack_site=None):
            """

            :param grid: int, 1-67.     labware location - carrier grid position
            :param site: int, 0 - 127.  labware location - (site on carrier - 1) !!!!!
            :param label:
            """

            self.rack = rack
            self.grid=grid
            self.site=site
            self.rack_site = rack_site

    class Position:
        def __init__(self, row, col=1):
            self.row=row
            self.col=col

    def autoselect(self, offset, maxTips=1, replys=1):
        nWells=self.type.nCol*self.type.nRow
        assert nWells>offset, "Can not select to far"   # todo better msg
        if self.type.conectedWells:
            if nWells<maxTips: maxTips=nWells
            self.selectOnly(range((nWells-maxTips)//2,maxTips))
            return maxTips
        else:
            if maxTips > replys: maxTips=replys
            self.selectOnly(range(offset,offset+maxTips))
            return maxTips

    def offset(self, row, col=1):
        if isinstance(row, Labware.Position):
            col=row.col
            row=row.row
        if isinstance(row,str):
            return self.offsetFromName(row)
        return row-1 + (col-1)*self.type.nRow

    def offsetFromName(self, wellName):
        row = ord(wellName[0]) - ord('A') + 1
        col = int(wellName[1:])
        return self.offset(row,col)

    def position(self, offset):
        return self.Position( offset % self.type.nCol + 1, offset // self.type.nCol + 1)

    def __init__(self, type, location, label=None, worktable=curWorkTable):
        self.type = type
        self.label=label
        self.location = location
        self.Wells = [Well(self,offset) for offset in range(self.offset(self.type.nRow,self.type.nCol)+1)]
        worktable.addLabware(self)
        if location.rack:
            location.rack.addLabware(self,location.rack_site)


    def clearSelection(self):
        for well in self.Wells:
            well.selFlag = False
        return self

    def selected(self):
        return [well.offset for well in self.Wells if well.selFlag]

    def selectAll(self):
        for well in self.Wells:
            well.selFlag = True
        return self

    def selectOnly(self,sel_idx_list):
        self.clearSelection()
        self.select(sel_idx_list)
        return self

    def select(self, sel_idx_list):
        for i in sel_idx_list:
            self.Wells[i].selFlag = True
        return self

    def newOffset(self, pos, offset ):
        return self.offset(pos.row,pos.col) + offset

    def newPosition(self, pos, offset):
        return self.position(self.newOffset(pos,offset))

    def posAtParallelMove(self, step):
        assert step < self.type.nCol * self.type.nRow , "too many steps!!"
        from Robot import curRobot
        #assert isinstance(curRobot,Robot.Robot)
        nTips = curRobot.curArm().nTips
        SubPlateSize = nTips * self.type.nCol
        SubPlate = step // SubPlateSize
        tN_semiCol  = step // nTips
        parit= (tN_semiCol//self.type.nCol)%2
        pos_semiCol = self.type.nCol*parit + (tN_semiCol%self.type.nCol)*(-1)**parit + 1
        p = self.Position(   row = SubPlate*nTips + step % nTips + 1,  col = pos_semiCol)
                             #col = self.type.nCol - (step//nTips) % self.type.nCol )
        return p

    def offsetAtParallelMove(self, step):
        p = self.posAtParallelMove(step)
        return self.offset(p.row, p.col)

    def moveParallel(self, pos, offset): # TODO
        return offset % self.type.nCol + 1, offset // self.type.nCol + 1

    def wellSelectionStr(self):
        """
        :return: See A.15.3, pag. A-122
        file:///C:/Prog/RobotEvo/FreedomEVOwareStandardV2.4SP1-2011.ExtendedDeviceSupportManual.pdf
        this function stores 7 bit per character in the selection string
        the first 2 characters are the number of wells in x direction (columns) in hexadecimal.
        the characters 3 and 4 are the number of wells in y direction (rows) in hexadecimal.
        well are computed in the order back to front, left to right;
        https://docs.python.org/3.4/library/string.html#formatstrings
        """
        X = self.type.nCol
        Y = self.type.nRow
        sel = "{:02X}{:02X}".format (X,Y)
        bitMask=0
        null = ord('0')
        bit=0
        for w in self.Wells:
            bit = w.offset % 7
            if w.selFlag: bitMask |=  (1<<bit)
            if bit == 6 :
                sel+= chr(null + bitMask)
                bitMask = 0
        if bit != 6:
            sel+= chr(null + bitMask)
        return sel


class Cuvette(Labware):
    pass

class Te_Mag(Labware):
    pass



Trough_100ml  = Labware.Type("Trough 100ml", 8, maxVol=100000,conectedWells=True )

EppRack16_2mL = Labware.Type("Tube Eppendorf 2mL 16 Pos", 16, maxVol=2000)

EppRack3x16R  = Labware.Type("Tube Eppendorf 3x 16 PosR", 3*16, maxVol=1500)

EppRack3x16   = Labware.Type("Tube Eppendorf 3x 16 Pos", 3*16, maxVol=1500)

TeMag48       = Labware.Type("Tube Eppendorf 48 Pos", 8, 6, maxVol=1500)

CleanerSWS    = Labware.Type("Washstation 2Grid Cleaner short"  , 8, maxVol=100000,conectedWells=True)
WashCleanerS  = Labware(CleanerSWS, Labware.Location(22,0))

WasteWS       = Labware.Type("Washstation 2Grid Waste"          , 8, maxVol=100000,conectedWells=True)
WashWaste     = Labware(WasteWS,    Labware.Location(22,1))

CleanerLWS    = Labware.Type("Washstation 2Grid Cleaner long"   , 8, maxVol=100000,conectedWells=True)
WashCleanerL  = Labware(CleanerLWS, Labware.Location(22,2))

DiTi_Waste    = Labware.Type("Washstation 2Grid DiTi Waste"     , 8, maxVol=100000,conectedWells=True)
DiTiWaste     = Labware(DiTi_Waste,Labware.Location(22,6))

DiTi_1000ul   = Labware.Type("DiTi 1000ul"     , 8,12, maxVol=970)



MP96well = Labware.Type("MP 96 well 0,2 mL", 8,12, maxVol=200)
