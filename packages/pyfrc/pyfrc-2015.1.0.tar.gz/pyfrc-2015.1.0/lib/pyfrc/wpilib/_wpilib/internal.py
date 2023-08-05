'''
    This module can be accessed via wpilib.internal, or via the
    'control' parameter to a test function::

        import wpilib.internal

        # enables the robot.. 
        wpilib.internal.enabled = True

    These functions/variables are the core engine that controls
    the operation of your robot code during simulation and during
    testing. Unit tests can use these functions/variables to cause
    the robot to do whatever things the test needs.

    Example tests that use these can be found in :mod:`pyfrc.tests`
'''

import inspect
import os
import sys


#################################################
#
# Core engine that controls the robot code
#
#################################################    

#: As a shortcut, you can assign to this variable to enable/disable the
#: robot instead of overriding on_IsEnabled
enabled = False
    
# assign functions to the on_* variables below in the test program to be 
# called when something happens in the robot code. The return value will 
# be given to the robot code.

# The 'tm' argument returns the value of GetClock(), which is the time
# that has been elapsed

#: Assign a function to this to determine if the robot is in autonomous
#: mode. The function should take a single parameter (current_time), and
#: return True if in autonomous mode, False otherwise
on_IsAutonomous         = None

#: Assign a function to this to determine if the robot is in teleoperated
#: mode. The function should take a single parameter (current_time), and
#: return True if in teleoperated mode, False otherwise
on_IsOperatorControl    = None

#: Assign a function to this to determine if the robot is enabled. The
#: function should take a single parameter (current_time), and return
#: True if in autonomous mode, False otherwise
on_IsEnabled            = None

#: Assign a function to this to determine if the robot is in test
#: mode. The function should take a single parameter (current_time), and
#: return True if in test mode, False otherwise.
on_IsTest               = None

on_IsSystemActive       = None
on_IsNewDataAvailable   = None

#######################################################################
#
# Another useful shortcut. You can define an object that has an
# IsAutonomous, etc function, which will be called when appropriate. 
#
#######################################################################








#################################################
#
# robot testing code
#
#################################################  



def _default_isAutonomous(tm):
    if enabled and on_IsEnabled is _default_isEnabled:
        raise RuntimeError("Your test will run infinitely! Call wpilib.internal.set_test_controller to control IsEnabled or IsAutonomous")
    return False

def _default_isOperatorControl(tm):
    if enabled and on_IsEnabled is _default_isEnabled:
        raise RuntimeError("Your test will run infinitely! Call wpilib.internal.set_test_controller to control IsEnabled or IsOperatorControl")
    return False

def _default_isEnabled(tm):
    if on_IsAutonomous is _default_isAutonomous and on_IsOperatorControl is _default_isOperatorControl:
        raise RuntimeError("Your test may run infinitely! Call wpilib.internal.set_test_controller to control the robot")
    
    return enabled


def initialize_test():
    '''Resets all wpilib globals'''
    
    this = sys.modules[__name__]
    
    setattr(this, 'enabled', False)
    
    setattr(this, 'on_IsAutonomous',        _default_isAutonomous)
    setattr(this, 'on_IsOperatorControl',   _default_isOperatorControl)
    setattr(this, 'on_IsEnabled',           _default_isEnabled)
    setattr(this, 'on_IsTest',              lambda: False)
    
    setattr(this, 'on_IsSystemActive',      lambda: True)
    setattr(this, 'on_IsNewDataAvailable',  lambda: True)
    
    from ._core import _StartCompetition
    from ... import wpilib
    
    wpilib.IterativeRobot.StartCompetition = _StartCompetition
    wpilib.SimpleRobot.StartCompetition = _StartCompetition
    
    # reset internal modules
    for name, cls in inspect.getmembers(wpilib, inspect.isclass):
        if hasattr(cls, '_reset'):
            cls._reset()
    
    
    # reset time
    from ._fake_time import FAKETIME
    FAKETIME.Reset()


def load_module(calling_file, relative_module_to_load):
    '''
        Utility function to be used to load a module that isn't in your python
        path. Can be useful if you're creating multiple testing robot programs
        and you don't want to copy modules from your main code to test them
        individually. 
    
        This should be called like so::
        
            module = load_module( __file__, '/../../relative/path/to/module.py' )
    
    '''
    
    import imp
 
    module_filename = os.path.normpath( os.path.join(os.path.dirname(os.path.abspath(calling_file)),relative_module_to_load))
    module_name = os.path.basename( os.path.splitext(module_filename)[0] )
    return imp.load_source( module_name, module_filename )
    
    
def print_components():
    '''
        Debugging function, prints out the components currently on the robot
    '''
    
    from . import AnalogModule, CAN, DigitalModule, DriverStation 
    
    AnalogModule._print_components()
    CAN._print_components()
    DigitalModule._print_components()
    DriverStation.GetInstance().GetEnhancedIO()._print_components()
    
    
#
# Utility functions for working with IterativeRobot
#

def IterativeRobotAutonomous(robot):
    
    from ... import wpilib
    
    robot.AutonomousInit()
    
    while robot.IsEnabled() and robot.IsAutonomous():
        robot.AutonomousPeriodic()
        
        if robot._period > 0:
            wpilib.Wait(robot._period)
        else:
            wpilib.Wait(0.20)
    
    
def IterativeRobotDisabled(robot, loops=None):
    
    from ... import wpilib
    
    robot.DisabledInit()
    
    i = 0
    while robot.IsDisabled():
        if loops is not None:
            if i >= loops:
                break
        
        i += 1
        robot.DisabledPeriodic()
        
        if robot._period > 0:
            wpilib.Wait(robot._period)
        else:
            wpilib.Wait(0.20)
    
    
def IterativeRobotTeleop(robot):
    
    from ... import wpilib
    
    robot.TeleopInit()
    
    while robot.IsOperatorControl() and robot.IsEnabled():
        robot.TeleopPeriodic()
        
        if robot._period > 0:
            wpilib.Wait(robot._period)
        else:
            wpilib.Wait(0.20)


#################################################
#
# physics simulation global singleton
#
#################################################  

from ...physics.core import Physics

#: Physics simulation global singleton (an instance of
#: :class:`pyfrc.physics.core.Physics`)
physics_controller = Physics()


