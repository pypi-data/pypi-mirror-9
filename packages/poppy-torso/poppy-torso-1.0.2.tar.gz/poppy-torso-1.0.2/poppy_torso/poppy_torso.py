import numpy

from functools import partial

from poppy.creatures import AbstractPoppyCreature

from .primitives.safe import LimitTorque
from .primitives.dance import SimpleBodyBeatMotion
#from .primitives.posture import StandPosition, SitPosition
from .primitives.idle import UpperBodyIdleMotion, HeadIdleMotion
from .primitives.interaction import ArmsTurnCompliant, PuppetMaster


class PoppyTorso(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        robot._primitive_manager._filter = partial(numpy.sum, axis=0)

        if robot.simulated:
            cls.vrep_hack(robot)
        for m in robot.motors:
            m.compliant_behavior = 'safe'
            m.goto_behavior = 'minjerk'

        #robot.attach_primitive(StandPosition(robot), 'stand_position')
        #robot.attach_primitive(SitPosition(robot), 'sit_position')

        robot.attach_primitive(LimitTorque(robot), 'limit_torque')

        robot.attach_primitive(SimpleBodyBeatMotion(robot, 50), 'dance_beat_motion')

        # robot.limit_torque.start()

        # Idle primitives
        robot.attach_primitive(UpperBodyIdleMotion(robot, 50), 'upper_body_idle_motion')
        robot.attach_primitive(HeadIdleMotion(robot, 50), 'head_idle_motion')

        # Interaction primitives
        robot.attach_primitive(ArmsTurnCompliant(robot, 50), 'arms_turn_compliant')
        robot.attach_primitive(PuppetMaster(robot, 50), 'arms_copy_motion')

    @classmethod
    def vrep_hack(cls, robot):
        # fix vrep orientation bug
        wrong_motor = [robot.bust_x, ]

        for m in wrong_motor:
            m.direct = not m.direct
            m.offset = -m.offset
