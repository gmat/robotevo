# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2016

__author__ = 'qPCR4vir'


import EvoScriPy.Labware as Lab
# from Robot import current
from EvoScriPy.Instruction_Base import def_liquidClass

def_react_excess =  4
def_mix_excess   =  8
NumOfSamples     = None

class Reactive:

    Reactives = None

    def __init__(self, name, labware,  volpersample=0, single_use=None,
                 pos=None, replicas=None, defLiqClass=None, excess=None, initial_vol=None):
        """
        Put a reactive into labware wells, possible with replicates and set the amount to be used for each sample

        :param name: str; Reactive name. Ex: "Buffer 1", "forward primer", "IC MS2"
        :param labware: Labware;
        :param volpersample: float; in uL
        :param pos: if not set (=None) we will try to assign consecutive wells for all the replicas
        :param replicas: int; def 1
        :param defLiqClass: str;
        :param excess: float; in %
        :param initial_vol: float; is set for each replica. If default (=None) is calculated als minimum.
        """
        if (Reactive.Reactives): Reactive.Reactives.Reactives.append(self)
        ex= def_react_excess if excess is None else excess
        self.excess = 1.0 + ex/100.0
        self.defLiqClass = defLiqClass or def_liquidClass
        self.name = name
        self.volpersample = volpersample
        self.labware = labware
        self.Replicas = labware.put(self, pos, replicas)
        self.pos = self.Replicas[0].offset
        if initial_vol is not None:
            for w in  self.Replicas:
                 w.vol += initial_vol
        if single_use:
            assert not volpersample, str(name) + \
                            ": this is a single use-reactive. Please, don't set any volume per sample."
            assert len(self.Replicas) == 1, "Temporally use only one vial for " + str(name)
            self.volpersample = single_use
            self.init_vol(NumSamples=1)
        else:
            self.init_vol()

    @staticmethod
    def SetReactiveList(protocol):
        Reactive.Reactives = protocol

    @staticmethod
    def StopReactiveList():
        Reactive.Reactives = None

    def __str__(self):
        return "{name:s}".format(name=self.name)

    def minVol(self, NumSamples=None)->float:
        NumSamples = NumSamples or NumOfSamples or 0
        return self.volpersample * NumSamples * self.excess

    def init_vol(self, NumSamples=None):
        self.put_min_vol(NumSamples)

    def put_min_vol(self, NumSamples=None):   # todo create replicas if needed !!!!
        NumSamples = NumSamples or NumOfSamples
        V = self.volpersample * self.excess
        replicas=len(self.Replicas)
        for i, w in enumerate(self.Replicas):
            v = V * (NumSamples + replicas - (i+1))//replicas
            if v > w.vol:  w.vol += (v-w.vol)

    def autoselect(self, maxTips=1):
        return self.labware.autoselect(self.pos, maxTips, len(self.Replicas))

class Reaction(Reactive):
    def __init__(self, name, track_sample, labware,
                 pos=None, replicas=None, defLiqClass=None, excess=None, initial_vol=None):
        Reactive.__init__(self, name, labware, single_use=0,
                 pos=pos, replicas=replicas, defLiqClass=defLiqClass, excess=excess, initial_vol=initial_vol)
        self.track_sample = track_sample


class preMix(Reactive):
    def __init__(self, name, labware, pos, components, replicas=1, initial_vol=None,
                 defLiqClass=None, excess=None):
        ex= def_mix_excess if excess is None else excess
        vol=0.0
        for react in components:
            vol += react.volpersample
            react.excess +=  ex/100.0      # todo revise! best to calculate at the moment of making?
            react.put_min_vol()

        if initial_vol is None: initial_vol = 0.0
        Reactive.__init__(self,name,labware,vol,pos=pos,replicas=replicas,
                          defLiqClass=defLiqClass,excess=ex, initial_vol=initial_vol)
        self.components = components

    def init_vol(self, NumSamples=None):
        pass # self.put_min_vol(NumSamples)


    def make(self, NumSamples=None):
        if self.Replicas[0].vol is None:   # ????
            self.put_min_vol(NumSamples)
            assert False
        from EvoScriPy.protocol_steps import makePreMix
        makePreMix(self, NumSamples)

    def compVol(self,index, NumSamples=None):
        NumSamples = NumSamples or NumOfSamples
        return self.components[index].minVol(NumSamples)



