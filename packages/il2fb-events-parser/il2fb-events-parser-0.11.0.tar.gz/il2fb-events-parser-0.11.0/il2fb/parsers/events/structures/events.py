# -*- coding: utf-8 -*-

import six

from il2fb.parsers.events.utils import translations

from . import Base


__all__ = (
    'AIAircraftHasDespawned', 'AIAircraftWasDamagedOnGround',
    'AIAircraftWasDamagedByAIAircraft', 'AIHasDamagedHisAircraft',
    'AIHasDestroyedHisAircraft', 'AIAircraftHasCrashed', 'AIAircraftHasLanded',
    'AIAircraftWasShotDownByStatic', 'AIAircraftWasDamagedByHumanAircraft',
    'AIAircraftWasShotDownByHumanAircraft',
    'AIAircraftWasShotDownByAIAircraft',
    'AIAircraftWasShotDownByMovingUnitMember',
    'AIAircraftCrewMemberWasWounded', 'AIAircraftCrewMemberWasHeavilyWounded',
    'AIAircraftCrewMemberHasBailedOut', 'AIAircraftCrewMemberHasTouchedDown',
    'AIAircraftCrewMemberWasKilled', 'AIAircraftCrewMemberWasKilledByStatic',
    'AIAircraftCrewMemberWasKilledByHumanAircraft',
    'AIAircraftCrewMemberWasKilledByAIAircraft',
    'AIAircraftCrewMemberWasKilledByMovingUnitMember',
    'AIAircraftCrewMemberWasKilledInParachuteByAIAircraft',
    'AIAircraftCrewMemberParachuteWasDestroyedByAIAircraft',
    'AIAircraftCrewMemberParachuteWasDestroyed',
    'AIAircraftCrewMemberWasCaptured',
    'BridgeWasDestroyedByHumanAircraft', 'BuildingWasDestroyedByHumanAircraft',
    'BuildingWasDestroyedByStatic', 'BuildingWasDestroyedByAIAircraft',
    'BuildingWasDestroyedByMovingUnit',
    'HumanAircraftWasDamagedByHumanAircraft',
    'HumanAircraftWasDamagedByStatic', 'HumanAircraftWasDamagedByAIAircraft',
    'HumanAircraftWasDamagedOnGround',
    'HumanAircraftWasShotDownByHumanAircraft',
    'HumanAircraftWasShotDownByStatic', 'HumanAircraftWasShotDownByAIAircraft',
    'HumanAircraftCrewMemberHasBailedOut',
    'HumanAircraftCrewMemberHasTouchedDown',
    'HumanAircraftCrewMemberWasCaptured',
    'HumanAircraftCrewMemberWasHeavilyWounded',
    'HumanAircraftCrewMemberWasKilled',
    'HumanAircraftCrewMemberWasKilledByHumanAircraft',
    'HumanAircraftCrewMemberWasKilledByStatic',
    'HumanAircraftCrewMemberWasWounded', 'HumanHasChangedSeat',
    'HumanHasDestroyedHisAircraft', 'HumanHasConnected',
    'HumanAircraftHasCrashed', 'HumanHasDamagedHisAircraft',
    'HumanHasDisconnected', 'HumanAircraftHasLanded',
    'HumanHasSelectedAirfield', 'HumanAircraftHasSpawned',
    'HumanHasToggledLandingLights', 'HumanHasToggledWingtipSmokes',
    'HumanAircraftHasTookOff', 'HumanHasWentToBriefing', 'MissionHasBegun',
    'MissionHasEnded', 'MissionIsPlaying', 'MissionWasWon',
    'StaticWasDestroyed', 'StaticWasDestroyedByStatic',
    'StaticWasDestroyedByAIAircraft', 'StaticWasDestroyedByHumanAircraft',
    'StaticWasDestroyedByMovingUnit', 'TargetStateWasChanged',
    'TreeWasDestroyedByHumanAircraft', 'TreeWasDestroyedByStatic',
    'TreeWasDestroyedByAIAircraft', 'TreeWasDestroyed',
    'MovingUnitWasDestroyedByStatic', 'MovingUnitWasDestroyedByMovingUnit',
    'MovingUnitWasDestroyedByMovingUnitMember',
    'MovingUnitMemberWasDestroyedByAIAircraft',
    'MovingUnitMemberWasDestroyedByHumanAircraft',
    'MovingUnitMemberWasDestroyedByMovingUnit',
    'MovingUnitMemberWasDestroyedByMovingUnitMember',
)

_ = translations.ugettext_lazy


class Event(Base):
    """
    Base event structure.
    """

    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs.get(key))
        super(Event, self).__init__()

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def verbose_name(self):
        raise NotImplementedError

    def to_primitive(self, context=None):
        primitive = super(Event, self).to_primitive(context)
        primitive.update({
            'name': self.name,
            'verbose_name': six.text_type(self.verbose_name),
        })
        return primitive

    def __repr__(self):
        return "<Event '{0}'>".format(self.name)


class MissionIsPlaying(Event):
    """
    Example::

        "[Sep 15, 2013 8:33:05 PM] Mission: PH.mis is Playing"
    """
    __slots__ = ['date', 'time', 'mission', ]
    verbose_name = _("Mission is playing")


class MissionHasBegun(Event):
    """
    Example::

        "[8:33:05 PM] Mission BEGIN"
    """
    __slots__ = ['time', ]
    verbose_name = _("Mission has begun")


class MissionHasEnded(Event):
    """
    Example::

        "[8:33:05 PM] Mission END"
    """
    __slots__ = ['time', ]
    verbose_name = _("Mission has ended")


class MissionWasWon(Event):
    """
    Example::

        "[Sep 15, 2013 8:33:05 PM] Mission: RED WON"
    """
    __slots__ = ['date', 'time', 'belligerent', ]
    verbose_name = _("Mission was won")


class TargetStateWasChanged(Event):
    """
    Example::

        "[8:33:05 PM] Target 3 Complete"
    """
    __slots__ = ['time', 'target_index', 'state', ]
    verbose_name = _("Target state was changed")


class HumanHasConnected(Event):
    """
    Example::

        "[8:33:05 PM] User0 has connected"
    """
    __slots__ = ['time', 'callsign', ]
    verbose_name = _("Human has connected")


class HumanHasDisconnected(Event):
    """
    Example::

        "[8:33:05 PM] User0 has disconnected"
    """
    __slots__ = ['time', 'callsign', ]
    verbose_name = _("Human has disconnected")


class HumanHasWentToBriefing(Event):
    """
    Example::

        "[8:33:05 PM] User0 entered refly menu"
    """
    __slots__ = ['time', 'callsign', ]
    verbose_name = _("Human has went to briefing")


class HumanHasSelectedAirfield(Event):
    """
    Example::

        "[8:33:05 PM] User0 selected army Red at 100.0 200.99"
    """
    __slots__ = ['time', 'callsign', 'belligerent', 'pos', ]
    verbose_name = _("Human has selected airfield")


class HumanHasToggledLandingLights(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 turned landing lights off at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'value', 'pos', ]
    verbose_name = _("Human has toggled landing lights")


class HumanHasToggledWingtipSmokes(Event):

    """
    Example::

        "[8:33:05 PM] User0:Pe-8 turned wingtip smokes off at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'value', 'pos', ]
    verbose_name = _("Human has toggled wingtip smokes")


class HumanHasChangedSeat(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) seat occupied by User0 at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("Human has changed seat")


class HumanAircraftHasSpawned(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 loaded weapons '40fab100' fuel 40%"
    """
    __slots__ = ['time', 'actor', 'weapons', 'fuel', ]
    verbose_name = _("Human aircraft has spawned")


class HumanAircraftHasTookOff(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 in flight at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("Human aircraft has took off")


class HumanAircraftHasLanded(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 landed at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("Human aircraft has landed")


class HumanAircraftHasCrashed(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 crashed at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human aircraft has crashed")


class HumanHasDestroyedHisAircraft(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 shot down by landscape at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human has destroyed his aircraft")


class HumanHasDamagedHisAircraft(Event):
    """
    Examples::

        "[8:33:05 PM] User0:Pe-8 damaged by landscape at 100.0 200.99"
        "[8:33:05 PM] User0:Pe-8 damaged by NONAME at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human has damaged his aircraft")


class HumanAircraftWasDamagedOnGround(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 damaged on the ground at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human aircraft was damaged on ground")


class HumanAircraftWasDamagedByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 damaged by User1:Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft was damaged by human aircraft")


class HumanAircraftWasDamagedByStatic(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 damaged by 0_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft was damaged by static")


class HumanAircraftWasDamagedByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 damaged by Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft was damaged by AI aircraft")


class HumanAircraftWasShotDownByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 shot down by User1:Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft was shot down by human aircraft")


class HumanAircraftWasShotDownByStatic(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8 shot down by 0_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft was shot down by static")


class HumanAircraftWasShotDownByAIAircraft(Event):
    """
    Event::

        "[8:33:05 PM] User0:Pe-8 shot down by Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft was shot down by AI aircraft")


class HumanAircraftCrewMemberHasBailedOut(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) bailed out at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("Human aircraft crew member has bailed out")


class HumanAircraftCrewMemberHasTouchedDown(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) successfully bailed out at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("Human aircraft crew member has touched down")


class HumanAircraftCrewMemberWasCaptured(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) was captured at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human aircraft crew member was captured")


class HumanAircraftCrewMemberWasWounded(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) was wounded at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human aircraft crew member was wounded")


class HumanAircraftCrewMemberWasHeavilyWounded(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) was heavily wounded at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human aircraft crew member was heavily wounded")


class HumanAircraftCrewMemberWasKilled(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) was killed at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Human aircraft crew member was killed")


class HumanAircraftCrewMemberWasKilledByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) was killed by User1:Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft crew member was killed by human aircraft")


class HumanAircraftCrewMemberWasKilledByStatic(Event):
    """
    Example::

        "[8:33:05 PM] User0:Pe-8(0) was killed by 0_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Human aircraft crew member was killed by static")


class BuildingWasDestroyedByHumanAircraft(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Buildings/Finland/CenterHouse1_w/live.sim destroyed by User0:Pe-8 at 100.0 200.99"
        "[8:33:05 PM] 3do/Buildings/Russia/Piter/House3_W/mono.sim destroyed by User1:Pe-8 at 300.0 400.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Building was destroyed by human aircraft")


class BuildingWasDestroyedByStatic(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Buildings/Finland/CenterHouse1_w/live.sim destroyed by 0_Static at 100.0 200.99"
        "[8:33:05 PM] 3do/Buildings/Russia/Piter/House3_W/mono.sim destroyed by 0_Static at 300.0 400.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Building was destroyed by static")


class BuildingWasDestroyedByMovingUnit(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Buildings/Finland/CenterHouse1_w/live.sim destroyed by 0_Chief at 100.0 200.99"
        "[8:33:05 PM] 3do/Buildings/Russia/Piter/House3_W/mono.sim destroyed by 0_Chief at 300.0 400.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Building was destroyed by moving unit")


class BuildingWasDestroyedByAIAircraft(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Buildings/Finland/CenterHouse1_w/live.sim destroyed by Bf-109G-6_Late at 100.0 200.99"
        "[8:33:05 PM] 3do/Buildings/Russia/Piter/House3_W/mono.sim destroyed by Bf-109G-6_Late at 300.0 400.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Building was destroyed by AI aircraft")


class TreeWasDestroyedByHumanAircraft(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Tree/Line_W/live.sim destroyed by User0:Pe-8 at 100.0 200.99"
        "[8:33:05 PM] 3do/Tree/Line_W/mono.sim destroyed by User0:Pe-8 at 100.0 200.99"
    """
    __slots__ = ['time', 'aggressor', 'pos', ]
    verbose_name = _("Tree was destroyed by human aircraft")


class TreeWasDestroyedByStatic(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Tree/Line_W/live.sim destroyed by 0_Static at 100.0 200.99"
        "[8:33:05 PM] 3do/Tree/Line_W/mono.sim destroyed by 0_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'aggressor', 'pos', ]
    verbose_name = _("Tree was destroyed by static")


class TreeWasDestroyedByAIAircraft(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Tree/Line_W/live.sim destroyed by Pe-8 at 100.0 200.99"
        "[8:33:05 PM] 3do/Tree/Line_W/mono.sim destroyed by Pe-8 at 100.0 200.99"
    """
    __slots__ = ['time', 'aggressor', 'pos', ]
    verbose_name = _("Tree was destroyed by AI aircraft")


class TreeWasDestroyed(Event):
    """
    Examples::

        "[8:33:05 PM] 3do/Tree/Line_W/live.sim destroyed by at 100.0 200.99"
        "[8:33:05 PM] 3do/Tree/Line_W/mono.sim destroyed by at 100.0 200.99"
    """
    __slots__ = ['time', 'pos', ]
    verbose_name = _("Tree was destroyed")


class StaticWasDestroyed(Event):
    """
    Example::

        "[8:33:05 PM] 0_Static crashed at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("Static was destroyed")


class StaticWasDestroyedByStatic(Event):
    """
    Example::

        "[8:33:05 PM] 0_Static destroyed by 1_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Static was destroyed by static")


class StaticWasDestroyedByMovingUnit(Event):
    """
    Example::

        "[8:33:05 PM] 0_Static destroyed by 0_Chief at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Static was destroyed by moving unit")


class StaticWasDestroyedByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] 0_Static destroyed by User0:Pe-8 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Static was destroyed by human aircraft")


class StaticWasDestroyedByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] 0_Static destroyed by Pe-8 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Static was destroyed by AI aircraft")


class BridgeWasDestroyedByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM]  Bridge0 destroyed by User0:Pe-8 at 100.0 200.99"

    Yes, there are 2 spaces before `Bridge0`.
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Bridge was destroyed by human aircraft")


class MovingUnitWasDestroyedByMovingUnit(Event):
    """
    Example::

        "[8:33:05 PM] 0_Chief destroyed by 1_Chief at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Moving unit was destroyed by moving unit")


class MovingUnitWasDestroyedByMovingUnitMember(Event):
    """
    Example::

        "[8:33:05 PM] 0_Chief destroyed by 1_Chief0 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Moving unit was destroyed by moving unit member")


class MovingUnitWasDestroyedByStatic(Event):
    """
    Example::

        "[8:33:05 PM] 0_Chief destroyed by 0_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Moving unit was destroyed by static")


class MovingUnitMemberWasDestroyedByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] 0_Chief0 destroyed by Pe-8 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Moving unit member was destroyed by AI aircraft")


class MovingUnitMemberWasDestroyedByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] 0_Chief0 destroyed by User0:Pe-8 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Moving unit member was destroyed by human aircraft")


class MovingUnitMemberWasDestroyedByMovingUnit(Event):
    """
    Example::

        "[8:33:05 PM] 0_Chief0 destroyed by 1_Chief at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Moving unit member was destroyed by moving unit")


class MovingUnitMemberWasDestroyedByMovingUnitMember(Event):
    """
    Example::

        "[8:33:05 PM] 0_Chief0 destroyed by 1_Chief0 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("Moving unit member was destroyed by moving unit member")


class AIAircraftHasDespawned(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 removed at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("AI aircraft has despawned")


class AIAircraftWasDamagedOnGround(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 damaged on the ground at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI aircraft was damaged on ground")


class AIAircraftWasDamagedByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 damaged by User1:Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft was damaged by human aircraft")


class AIAircraftWasDamagedByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 damaged by Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft was damaged by AI aircraft")


class AIHasDamagedHisAircraft(Event):
    """
    Examples::

        "[8:33:05 PM] Pe-8 damaged by landscape at 100.0 200.99"
        "[8:33:05 PM] Pe-8 damaged by NONAME at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI has damaged his aircraft")


class AIHasDestroyedHisAircraft(Event):
    """
    Examples::

        "[8:33:05 PM] Pe-8 shot down by landscape at 100.0 200.99"
        "[8:33:05 PM] Pe-8 shot down by NONAME at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI has destroyed his aircraft")


class AIAircraftHasCrashed(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 crashed at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI aircraft has crashed")


class AIAircraftWasShotDownByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 shot down by User1:Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft was shot down by human aircraft")


class AIAircraftWasShotDownByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 shot down by Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft was shot down by AI aircraft")


class AIAircraftWasShotDownByStatic(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 shot down by 0_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft was shot down by static")


class AIAircraftWasShotDownByMovingUnitMember(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 shot down by 0_Chief0 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft was shot down by moving unit member")


class AIAircraftHasLanded(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8 landed at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("AI aircraft has landed")


class AIAircraftCrewMemberWasKilled(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was killed at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI aircraft crew member was killed")


class AIAircraftCrewMemberWasKilledByStatic(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was killed by 0_Static at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft crew member was killed by static")


class AIAircraftCrewMemberWasKilledByHumanAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was killed by User0:Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft crew member was killed by human aircraft")


class AIAircraftCrewMemberWasKilledByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was killed by Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft crew member was killed by AI aircraft")


class AIAircraftCrewMemberWasKilledByMovingUnitMember(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was killed by 0_Chief0 at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft crew member was killed by moving unit "
                     "member")


class AIAircraftCrewMemberWasKilledInParachuteByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was killed in his chute by Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft crew member was killed in parachute "
                     "by AI aircraft")


class AIAircraftCrewMemberParachuteWasDestroyedByAIAircraft(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) has chute destroyed by Bf-109G-6_Late at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'aggressor', 'pos', ]
    verbose_name = _("AI aircraft crew member's parachute was destroyed "
                     "by AI aircraft")


class AIAircraftCrewMemberParachuteWasDestroyed(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) has chute destroyed by at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI aircraft crew member's parachute was destroyed")


class AIAircraftCrewMemberWasWounded(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was wounded at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI aircraft crew member was wounded")


class AIAircraftCrewMemberWasHeavilyWounded(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was heavily wounded at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI aircraft crew member was heavily wounded")


class AIAircraftCrewMemberWasCaptured(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) was captured at 100.0 200.99"
    """
    __slots__ = ['time', 'victim', 'pos', ]
    verbose_name = _("AI aircraft crew member was captured")


class AIAircraftCrewMemberHasBailedOut(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) bailed out at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("AI aircraft crew member has bailed out")


class AIAircraftCrewMemberHasTouchedDown(Event):
    """
    Example::

        "[8:33:05 PM] Pe-8(0) successfully bailed out at 100.0 200.99"
    """
    __slots__ = ['time', 'actor', 'pos', ]
    verbose_name = _("AI aircraft crew member has touched down")
