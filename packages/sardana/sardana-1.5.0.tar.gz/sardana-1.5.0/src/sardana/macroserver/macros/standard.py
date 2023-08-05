##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This is the standard macro module"""

__all__ = ["ct", "mstate", "mv", "mvr", "pwa", "pwm", "set_lim", "set_lm",
           "set_pos", "settimer", "uct", "umv", "umvr", "wa", "wm"] 

__docformat__ = 'restructuredtext'

import datetime
from taurus.console.table import Table

from PyTango import DevState
from sardana.macroserver.macro import Macro, macro, Type, ParamRepeat, ViewOption

################################################################################
#
# Motion related macros
#
################################################################################

class _wm(Macro):
    """Show motor positions"""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Moveable, None, 'Motor to move']),
         None, 'List of motor to show'],
    ]

    def prepare(self, *motor_list, **opts):
        self.table_opts = {}
    
    def run(self, *motor_list):
        show_dial = self.getViewOption(ViewOption.ShowDial)
        show_ctrlaxis = self.getViewOption(ViewOption.ShowCtrlAxis)
        pos_format = self.getViewOption(ViewOption.PosFormat)

        motor_width = 9
        motor_names = []
        motor_pos   = []
        motor_list = list(motor_list)
        motor_list.sort()
        for motor in motor_list:

            name = motor.getName()
            motor_names.append([name])

            pos = motor.getPosition(force=True)
            if pos is None:
                pos = float('NAN')
        
            # TODO: refactor this code, so the info tuple is progressively
            # expanded depending on the _ViewOptions, instead of repeating the 
            # code in the if/else statements
            if show_dial:
                dial_pos = motor.getDialPosition(force=True)
                if dial_pos is None:
                    dial_pos = float('NAN')
                if show_ctrlaxis:
                    ctrl_name = self.getController(motor.controller).name
                    axis_nb = getattr(motor, "axis")
                    motor_pos.append((ctrl_name, str(axis_nb), pos, dial_pos))
                else:
                    motor_pos.append((pos,dial_pos))
            else:
                if show_ctrlaxis:
                    ctrl_name = self.getController(motor.controller).name
                    axis_nb = getattr(motor, "axis")
                    motor_pos.append((ctrl_name, str(axis_nb), pos))
                else:
                    motor_pos.append((pos,))

            motor_width = max(motor_width,len(name))
            
            if show_ctrlaxis:
                motor_width = max(motor_width, len(ctrl_name), len(str(axis_nb)))
 
        fmt = '%c*.%df' % ('%',motor_width - 5)

        if pos_format > -1:
            fmt = '%c*.%df' % ('%',int(pos_format))

        row_head_str = []
        if show_ctrlaxis:
            row_head_str += ['Ctrl', 'Axis']
            if show_dial:
                t_format = ['%*s','%*s',fmt,fmt]
                row_head_str += ['User', 'Dial']
            else:
                t_format = ['%*s','%*s',fmt]
                row_head_str += ['User']
        else:
            if show_dial:
                t_format = [fmt, fmt]
            else:
                t_format = [fmt]

        row_head_str = row_head_str if len(row_head_str) else None 
        table = Table(motor_pos, elem_fmt=t_format,
                      col_head_str=motor_names, col_head_width=motor_width,
                      row_head_str=row_head_str, **self.table_opts)
        for line in table.genOutput():
            self.output(line)

class _wum(Macro):
    """Show user motor positions"""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Moveable, None, 'Motor to move']),
         None, 'List of motor to show'],
    ]

    def prepare(self, *motor_list, **opts):
        self.table_opts = {}
    
    def run(self, *motor_list):
        show_dial = self.getViewOption(ViewOption.ShowDial)
        motor_width = 9
        motor_names = []
        motor_pos   = []
        motor_list = list(motor_list)
        motor_list.sort()
        for motor in motor_list:
            name = motor.getName()
            motor_names.append([name])
            pos = motor.getPosition(force=True)
            if pos is None:
                pos = float('NAN')
            motor_pos.append((pos,))
            motor_width = max(motor_width,len(name))

        fmt = '%c*.%df' % ('%',motor_width - 5)

        table = Table(motor_pos, elem_fmt=[fmt],
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)
            
class wu(Macro):
    """Show all user motor positions"""

    def prepare(self, **opts):
        self.all_motors = self.findObjs('.*', type_class=Type.Moveable)
        self.table_opts = {}
    
    def run(self):
        nr_motors = len(self.all_motors)
        if nr_motors == 0:
            self.output('No motor defined')
            return
        
        self.output('Current positions (user) on %s'%datetime.datetime.now().isoformat(' '))
        self.output('')
        
        self.execMacro('_wum',*self.all_motors, **self.table_opts)

class wa(Macro):
    """Show all motor positions"""

    param_def = [
        ['filter',
         ParamRepeat(['filter', Type.String, '.*', 'a regular expression filter'], min=0, max=1),
         '.*', 'a regular expression filter'],
    ]

    def prepare(self, *filter, **opts):
        self.all_motors = self.findObjs(filter, type_class=Type.Moveable)
        self.table_opts = {}
    
    def run(self, *filter):
        nr_motors = len(self.all_motors)
        if nr_motors == 0:
            self.output('No motor defined')
            return
        
        show_dial = self.getViewOption(ViewOption.ShowDial)
        if show_dial:
            self.output('Current positions (user, dial) on %s'%datetime.datetime.now().isoformat(' '))
        else:
            self.output('Current positions (user) on %s'%datetime.datetime.now().isoformat(' '))
        self.output('')
        
        self.execMacro('_wm',*self.all_motors, **self.table_opts)


class pwa(Macro):
    """Show all motor positions in a pretty table"""

    param_def = [
        ['filter',
         ParamRepeat(['filter', Type.String, '.*', 'a regular expression filter'], min=0, max=1),
         '.*', 'a regular expression filter'],
    ]

    def run(self, *filter):
        self.execMacro('wa', *filter, **Table.PrettyOpts)

class set_lim(Macro):
    """Sets the software limits on the specified motor hello"""
    param_def = [
        ['motor', Type.Moveable, None, 'Motor name'],
        ['low',   Type.Float, None, 'lower limit'],
        ['high',   Type.Float, None, 'upper limit']
    ]
    
    def run(self, motor, low, high):
        name = motor.getName()
        self.debug("Setting user limits for %s" % name)
        motor.getPositionObj().setLimits(low,high)
        self.output("%s limits set to %.4f %.4f (user units)" % (name, low, high))

class set_lm(Macro):
    """Sets the dial limits on the specified motor"""
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['low',   Type.Float, None, 'lower limit'],
        ['high',   Type.Float, None, 'upper limit']
    ]
    
    def run(self, motor, low, high):
        name = motor.getName()
        self.debug("Setting dial limits for %s" % name)
        motor.getDialPositionObj().setLimits(low,high)
        self.output("%s limits set to %.4f %.4f (dial units)" % (name, low, high))
        
class set_pos(Macro):
    """Sets the position of the motor to the specified value"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['pos',   Type.Float, None, 'Position to move to']
    ]
    
    def run(self, motor, pos):
        name = motor.getName()
        old_pos = motor.getPosition(force=True)
        motor.definePosition(pos)
        self.output("%s reset from %.4f to %.4f" % (name, old_pos, pos))

class set_user_pos(Macro):
    """Sets the USER position of the motor to the specified value (by changing OFFSET and keeping DIAL)"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['pos',   Type.Float, None, 'Position to move to']
    ]
    
    def run(self, motor, pos):
        name = motor.getName()
        old_pos = motor.getPosition(force=True)
        offset_attr = motor.getAttribute('Offset')
        old_offset = offset_attr.read().value
        new_offset = pos - (old_pos - old_offset)
        offset_attr.write(new_offset)
        self.output("%s reset from %.4f (offset %.4f) to %.4f (offset %.4f)" % (name, old_pos, old_offset, pos, new_offset))

class wm(Macro):
    """Show the position of the specified motors."""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Moveable, None, 'Motor to see where it is']),
         None, 'List of motor to show'],
    ]

    def prepare(self, *motor_list, **opts):
        self.table_opts = {}
        
    def run(self, *motor_list):
        motor_width = 10
        motor_names = []
        motor_pos   = []

        show_dial = self.getViewOption(ViewOption.ShowDial)
        show_ctrlaxis = self.getViewOption(ViewOption.ShowCtrlAxis)
        pos_format = self.getViewOption(ViewOption.PosFormat)
 
        for motor in motor_list:
                   
            max_len = 0
            if show_ctrlaxis:
                axis_nb = getattr(motor, "axis")
                ctrl_name = self.getController(motor.controller).name
                max_len = max(max_len, len(ctrl_name), len(str(axis_nb)))
            name = motor.getName()
            max_len = max(max_len, len(name))

            max_len = max_len + 5
            if max_len < 14:
                max_len = 14 # Length of 'Not specified'

            str_fmt = "%c%ds" % ('%', int(max_len))

            name = str_fmt % name

            motor_names.append([name])
            posObj = motor.getPositionObj()
            if pos_format > -1:
                fmt = '%c.%df' % ('%', int(pos_format))

            try:
                val1 = fmt % motor.getPosition(force=True)
                val1 = str_fmt % val1
            except:
                val1 = str_fmt % motor.getPosition(force=True)
      

            val2 =  str_fmt % posObj.getMaxValue()
            val3 =  str_fmt % posObj.getMinValue()

            if show_ctrlaxis:
                valctrl = str_fmt % (ctrl_name)
                valaxis = str_fmt % str(axis_nb)
                upos = map(str, [valctrl, valaxis, ' ', val2, val1, val3])
            else:
                upos = map(str, ['', val2, val1, val3])
            pos_data =  upos
            if show_dial:
                try:
                    val1 = fmt % motor.getDialPosition(force=True)
                    val1 = str_fmt % val1
                except:
                    val1 = str_fmt % motor.getDialPosition(force=True)
     
                dPosObj = motor.getDialPositionObj() 
                val2 =  str_fmt % dPosObj.getMaxValue()
                val3 =  str_fmt % dPosObj.getMinValue()

                dpos = map(str, [val2, val1, val3])
                pos_data += [''] + dpos
            
            motor_pos.append(pos_data)

        elem_fmt = (['%*s'] + ['%*s'] * 5) * 2
        row_head_str = []
        if show_ctrlaxis:
            row_head_str += ['Ctrl', 'Axis']
        row_head_str += ['User', ' High', ' Current', ' Low']
        if show_dial:
            row_head_str += ['Dial', ' High', ' Current', ' Low']
        table = Table(motor_pos, elem_fmt=elem_fmt, row_head_str=row_head_str,
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)

class wum(Macro):
    """Show the user position of the specified motors."""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Moveable, None, 'Motor to see where it is']),
         None, 'List of motor to show'],
    ]

    def prepare(self, *motor_list, **opts):
        self.table_opts = {}
        
    def run(self, *motor_list):
        motor_width = 10
        motor_names = []
        motor_pos   = []
        
        for motor in motor_list:
            name = motor.getName()
            motor_names.append([name])
            posObj = motor.getPositionObj()
            upos = map(str, [posObj.getMaxValue(), motor.getPosition(force=True), posObj.getMinValue()])
            pos_data = [''] + upos
            
            motor_pos.append(pos_data)

        elem_fmt = (['%*s'] + ['%*s'] * 3) * 2
        row_head_str = ['User', ' High', ' Current', ' Low',]
        table = Table(motor_pos, elem_fmt=elem_fmt, row_head_str=row_head_str,
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)
            
class pwm(Macro):
    """Show the position of the specified motors in a pretty table"""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Moveable, None, 'Motor to move']),
         None, 'List of motor to show'],
    ]

    def run(self, *motor_list):
        self.execMacro('wm', *motor_list, **Table.PrettyOpts)

class mv(Macro):
    """Move motor(s) to the specified position(s)"""

    param_def = [
       ['motor_pos_list',
        ParamRepeat(['motor', Type.Moveable, None, 'Motor to move'],
                    ['pos',   Type.Float, None, 'Position to move to']),
        None, 'List of motor/position pairs'],
    ]

    def run(self, *motor_pos_list):
        motors, positions = [], []
        for motor, pos in motor_pos_list:
            motors.append(motor)
            positions.append(pos)
            self.debug("Starting %s movement to %s", motor.getName(), pos)
        motion = self.getMotion(motors)
        state, pos = motion.move(positions)
        if state != DevState.ON:
            self.warning("Motion ended in %s", state)
            msg = []
            for motor in motors:
                msg.append(motor.information())
            self.info("\n".join(msg))

class mstate(Macro):
    """Prints the state of a motor"""
    
    param_def = [['motor', Type.Moveable, None, 'Motor to check state']]

    def run(self, motor):
        self.info("Motor %s" % str(motor.getState()))

class umv(Macro):
    """Move motor(s) to the specified position(s) and update"""

    param_def = mv.param_def

    def prepare(self, *motor_pos_list, **opts):
        self.all_names = []
        self.all_pos = []
        self.print_pos = False
        for motor, pos in motor_pos_list:
            self.all_names.append([motor.getName()])
            pos, posObj = motor.getPosition(force=True), motor.getPositionObj()
            self.all_pos.append([pos])
            posObj.subscribeEvent(self.positionChanged, motor)
        
    def run(self, *motor_pos_list):
        self.print_pos = True
        pars = []
        for motor, pos in motor_pos_list:
            pars.append(motor)
            pars.append(pos)

        self.execMacro('mv', *pars)
        self.finish()
 
    def finish(self):
        self._clean()
        self.printAllPos()
 
    def on_abort(self):
        self.finish()
        
    def _clean(self):
        for motor, pos in self.getParameters():
            posObj = motor.getPositionObj()
            try:
                posObj.unsubscribeEvent(self.positionChanged, motor)
            except Exception, e:
                print str(e)
                raise e
    
    def positionChanged(self, motor, position):
        idx = self.all_names.index([motor.getName()])
        self.all_pos[idx] = [position]
        if self.print_pos:
            self.printAllPos()
    
    def printAllPos(self):
        motor_width = 10
        table = Table(self.all_pos, elem_fmt=['%*.4f'],
                      col_head_str=self.all_names, col_head_width=motor_width)
        self.outputBlock(table.genOutput())
        self.flushOutput()

class mvr(Macro):
    """Move motor(s) relative to the current position(s)"""

    param_def = [
       ['motor_disp_list',
        ParamRepeat(['motor', Type.Moveable, None, 'Motor to move'],
                    ['disp',  Type.Float, None, 'Relative displacement']),
        None, 'List of motor/displacement pairs'],
    ]
    
    def run(self, *motor_disp_list):
        motor_pos_list = []
        for motor, disp in motor_disp_list:
            pos = motor.getPosition(force=True) 
            if pos is None:
                self.error("Cannot get %s position" % motor.getName())
                return
            else:
                pos += disp
            motor_pos_list.extend([motor, pos])
        self.execMacro('mv', *motor_pos_list)

class umvr(Macro):
    """Move motor(s) relative to the current position(s) and update"""

    param_def = mvr.param_def

    def run(self, *motor_disp_list):
        motor_pos_list = []
        for motor, disp in motor_disp_list:
            pos = motor.getPosition(force=True) 
            if pos is None:
                self.error("Cannot get %s position" % motor.getName())
                return
            else:
                pos += disp
            motor_pos_list.extend([motor, pos])
        self.execMacro('umv', *motor_pos_list)


################################################################################
#
# Data acquisition related macros
#
################################################################################


class ct(Macro):
    """Count for the specified time on the active measurement group"""

    env = ('ActiveMntGrp',)

    param_def = [
       ['integ_time', Type.Float, 1.0, 'Integration time']
    ]

    def prepare(self, integ_time, **opts):
        mnt_grp_name = self.getEnv('ActiveMntGrp')
        self.mnt_grp = self.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)

    def run(self, integ_time):
        if self.mnt_grp is None:
            self.error('ActiveMntGrp is not defined or has invalid value')
            return

        self.debug("Counting for %s sec", integ_time)
        self.outputDate()
        self.output('')
        self.flushOutput()

        state, data = self.mnt_grp.count(integ_time)

        names, counts = [], []
        for ch_info in self.mnt_grp.getChannelsInfo():
            names.append('  %s' % ch_info.label)
            ch_data = data.get(ch_info.full_name)
            if ch_info.shape > [1]:
                counts.append(list(ch_data.shape))
            else:
                counts.append(ch_data)
        
        table = Table([counts], row_head_str=names, row_head_fmt='%*s',
                      col_sep='  =  ')
        for line in table.genOutput():
            self.output(line)


class uct(Macro):
    """Count on the active measurement group and update"""

    env = ('ActiveMntGrp',)

    param_def = [
       ['integ_time', Type.Float, 1.0, 'Integration time']
    ]

    def prepare(self, integ_time, **opts):
        
        self.print_value = False
        
        mnt_grp_name = self.getEnv('ActiveMntGrp')
        self.mnt_grp = self.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)

        if self.mnt_grp is None:
            return

        names, nan = self.mnt_grp.getChannelLabels(), float('nan')
        self.names    = [ [n] for n in names ]
        
        self.values   = len(names)*[ [nan] ]
        self.channels = self.mnt_grp.getChannelAttrExs()

        for ch_attr_ex in self.channels:
            ch_attr_ex.subscribeEvent(self.counterChanged, ch_attr_ex)

    def printAllValues(self):
        ch_width = 10
        table = Table(self.values, elem_fmt=['%*.4f'], col_head_str=self.names, 
                      col_head_width=ch_width)
        self.outputBlock(table.genOutput())
        self.flushOutput()
    
    def counterChanged(self, ch_attr, value):
        idx = self.channels.index(ch_attr)
        self.values[idx] = [value]
        if self.print_value:
            self.printAllValues()
        
    def run(self, integ_time):
        if self.mnt_grp is None:
            self.error('ActiveMntGrp is not defined or has invalid value')
            return
        
        self.print_value = True
        
        state, data = self.mnt_grp.count(integ_time)

        for ch_attr_ex in self.mnt_grp.getChannelAttrExs():
            ch_attr_ex.unsubscribeEvent(self.counterChanged, ch_attr_ex)
        self.printAllValues()


class settimer(Macro):
    """Defines the timer channel for the active measurement group"""
    
    env = ('ActiveMntGrp',)
    
    param_def = [
       ['timer', Type.ExpChannel,   None, 'Timer'],
    ]
    
    def run(self,timer):
        mnt_grp_name = self.getEnv('ActiveMntGrp')
        mnt_grp = self.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)

        if mnt_grp is None:
            self.error('ActiveMntGrp is not defined or has invalid value.\n' \
                       'please define a valid active measurement group ' \
                       'before setting a timer')
            return
        
        try:
            mnt_grp.setTimer(timer.getName())
        except Exception,e:
            self.output(str(e))
            self.output("%s is not a valid channel in the active measurement group" % timer)

@macro([['message', ParamRepeat(['message_item', Type.String, None, 'message item to be reported']), None, 'message to be reported']])
def report(self, *message):
    """Logs a new record into the message report system (if active)"""
    self.report(' '.join(message))

