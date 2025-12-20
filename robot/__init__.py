# robot/__init__.py
"""
Robot package initializer.
This allows you to import robot classes directly from robot.
"""

from .robot_base import RobotBase
from .robot_r1 import RobotR1
from .robot_r2 import RobotR2
from .robot_r3 import RobotR3

__all__ = ["RobotBase", "RobotR1", "RobotR2", "RobotR3"]