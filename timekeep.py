#!/usr/bin/env python
from __future__ import division

import pygtk
pygtk.require('2.0')
import gtk
import os
from time import time
from math import floor
gtk.gdk.threads_init()
import gobject
from datetime import datetime
from subprocess import call

#Parameters
MIN_WORK_TIME = 60 * 10 # min work time in seconds

"""
class EntryDialog(gtk.MessageDialog):
    def __init__(self, *args, **kwargs):
        '''
        Creates a new EntryDialog. Takes all the arguments of the usual
        MessageDialog constructor plus one optional named argument 
        "default_value" to specify the initial contents of the entry.
        '''
        if 'default_value' in kwargs:
            default_value = kwargs['default_value']
            del kwargs['default_value']
        else:
            default_value = ''
        super(EntryDialog, self).__init__(*args, **kwargs)
        entry = gtk.Entry()        
        entry.set_text(str(default_value))
        entry.connect("activate", 
                      lambda ent, dlg, resp: dlg.response(resp), 
                      self, gtk.RESPONSE_OK)
        self.vbox.pack_end(entry, True, True, 0)
        self.vbox.show_all()
        self.entry = entry
    def set_value(self, text):
        self.entry.set_text(text)
    def run(self):
        result = super(EntryDialog, self).run()
        if result == gtk.RESPONSE_OK:
            text = self.entry.get_text()
        else:
            text = None
        return text
"""   
     
def get_text(parent, message, default=''):
    """
    Display a dialog with a text entry.
    Returns the text, or None if canceled.
    """
    d = gtk.MessageDialog(parent,
                          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_QUESTION,
                          gtk.BUTTONS_OK_CANCEL,
                          message)
    entry = gtk.Entry()
    entry.set_text(default)
    entry.show()
    d.vbox.pack_end(entry)
    entry.connect('activate', lambda _: d.response(gtk.RESPONSE_OK))
    d.set_default_response(gtk.RESPONSE_OK)

    r = d.run()
    text = entry.get_text().decode('utf8')
    d.destroy()
    if r == gtk.RESPONSE_OK:
        return text
    else:
        return None

class TimeKeep:
    """
    Rings a bell (play a sound) every set number of minutes
    with the ability to set some "sleep" time every day
    """
    def __init__(self):
        self.icon=gtk.status_icon_new_from_file(self.icon_directory()+"idle.png")
        self.icon.set_tooltip("Idle")
        self.state = "idle"
        self.tick_interval=10 #number of seconds between each poll
        self.icon.connect('activate',self.icon_click)
        self.icon.connect('popup-menu', self.right_click_event)
        self.icon.set_visible(True)
        self.start_working_time = 0
        self.min_work_time = MIN_WORK_TIME
        self.start_time = datetime(1900,1,1,8,0,0)
        self.end_time = datetime(1900,1,1,22,0,0)
        self.sound_file = self.icon_directory()+"warning.wav"
        self.dbg = True
    def format_time(self,seconds):
        minutes = floor(seconds / 60)
        if minutes > 1 or minutes < 1:
            return "%d minutes" % minutes
        else:
            return "%d minute" % minutes
    def set_state(self,state):
        old_state=self.state
        self.icon.set_from_file(self.icon_directory()+state+".png")
        if state == "idle":
            delta = time() - self.start_working_time
#            if old_state == "ok":
#                self.icon.set_tooltip("Good! Worked for %s." % 
#                        self.format_time(delta))
#            elif old_state == "working":
#                self.icon.set_tooltip("Not good: worked for only %s." % 
#                        self.format_time(delta))
            self.icon.set_tooltip("Idle")
        else:
            if state == "working":
                self.start_working_time = time()
            delta = time() - self.start_working_time
            self.icon.set_tooltip("Next bell in %s" % self.format_time(self.min_work_time - delta))
        self.state=state
    def icon_directory(self):
        return os.path.dirname(os.path.realpath(__file__)) + os.path.sep
    def icon_click(self,dummy):
        delta = time() - self.start_working_time
        if self.state == "idle":
            self.set_state("working")
        else:
            self.set_state("idle")
    def right_click_event(self, icon, button, time):
        menu = gtk.Menu()

        about = gtk.MenuItem("About")
        quit = gtk.MenuItem("Quit")
        
        timespan = gtk.MenuItem("Time Span")
        starttime = gtk.MenuItem("Start Time")
        endtime = gtk.MenuItem("End Time")
        
        about.connect("activate", self.show_about_dialog)
        quit.connect("activate", gtk.main_quit)
        timespan.connect("activate", self.set_time_span)
        starttime.connect("activate", self.set_start_time)
        endtime.connect("activate", self.set_end_time)
        
        menu.append(timespan)
        menu.append(starttime)
        menu.append(endtime)
        menu.append(about)
        menu.append(quit)
        
        menu.show_all()
        
        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.icon)
    def update(self):
        """This method is called everytime a tick interval occurs"""
#        call(["/usr/bin/aplay","-q",self.sound_file])
        delta = time() - self.start_working_time
        if self.state == "idle":
            pass
        elif self.state == "working":
            self.icon.set_tooltip("Next bell in %s" % self.format_time(self.min_work_time - delta))
            if delta > self.min_work_time:
                call(["/usr/bin/aplay","-q",self.sound_file])
                self.set_state("working")
            if datetime.now().time() > self.end_time.time():
                self.set_state("ok")
        else:
            self.icon.set_tooltip("Bell resuming at %s" % self.start_time.strftime("%H:%M"))
            if datetime.now().time() > self.start_time.time() and datetime.now().time() < self.end_time.time():
                self.set_state("working")
        source_id = gobject.timeout_add(self.tick_interval*1000, self.update)
    def show_about_dialog(self, widget):
        about_dialog = gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("Time Keep")
        about_dialog.set_version("0.1")
        about_dialog.set_authors(["Jorge Blanco"])
        		
        about_dialog.run()
        about_dialog.destroy()
    def error_message(self, message):
        md = gtk.MessageDialog(None, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
            gtk.BUTTONS_CLOSE, message)
        md.run()
        md.destroy()
    def set_time_span(self, widget):
        try:
            mt = int(self.min_work_time / 60)
            time_span = int(get_text(None,"How often should the bell ring? (Every X minutes)",str(mt)))
            self.min_work_time = time_span*60
        except ValueError:
            self.error_message("Please input a number")
        except TypeError:
            if self.dbg:
                raise
            else:
                pass #User cancelled
    def set_start_time(self, widget):
        try:
            start = get_text(None,"When should the bell start? (In 24h format)",self.start_time.strftime("%H:%M"))
            self.start_time = datetime.strptime(start,"%H:%M")
        except ValueError:
            try:
                self.start_time = datetime.strptime(start,"%H")
            except ValueError:
                self.error_message("Please input a time (e.g. 8:00, or 8)")
        except TypeError:
            if self.dbg:
                raise
            else:
                pass #User cancelled
    def set_end_time(self, widget):
        try:
            end = get_text(None,"When should the bell stop? (In 24h format)",self.end_time.strftime("%H:%M"))
            self.end_time = datetime.strptime(end,"%H:%M")
        except ValueError:
            try:
                self.end_time = datetime.strptime(end,"%H")
            except ValueError:
                self.error_message("Please input a time (e.g. 22:00, or 22)")
        except TypeError:
            if self.dbg:
                raise
            else:
                pass #User cancelled
    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        source_id = gobject.timeout_add(self.tick_interval, self.update)
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a Pomodoro instance and show it
if __name__ == "__main__":
    app = TimeKeep()
    app.main()
