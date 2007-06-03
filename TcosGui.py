# -*- coding: UTF-8 -*-
##########################################################################
# tcos_config writen by MarioDebian <mariodebian@gmail.com>
#
#    TcosConfig version __VERSION__
#
# Copyright (c) 2005 Mario Izquierdo <mariodebian@gmail.com>
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

from ConfigReader import *
import shared

from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import os, shutil
#import sys, re
import pygtk
pygtk.require('2.0')
import gtk.glade
import time
from gettext import gettext as _




def print_debug(txt):
    global debug
    if shared.debug:
        print ( "DEBUG %s " %(txt) )

    



class TcosGui:
    def __init__(self):
        import shared

        # load some classes
        self.tcos_config_file = shared.tcos_config_file
        self.config=ConfigReader()
        #print_debug ("init gui class")

        # delete tcos.conf.orig file if exits
        abspath = os.path.abspath(self.tcos_config_file)
        destfile= abspath + ".orig"

        try:
            os.remove(destfile)
            print_debug ("TcosGui::__init__ deleting old tcos.conf.orig")
        except:
            print_debug("TcosGui::__init__ old tcos.conf.orig not found")
            pass

        self.step=0

        # glade locale init
        gtk.glade.bindtextdomain(shared.PACKAGE, shared.LOCALE_DIR)
        gtk.glade.textdomain(shared.PACKAGE)

        # Widgets
        self.ui = gtk.glade.XML(shared.GLADE_DIR + 'tcosconfig.glade')

        # load all widgets
        for widget in self.ui.get_widget_prefix(""):
            setattr(self, widget.get_name(), widget)

        self.aboutdialog = self.ui.get_widget("aboutdialog")
        self.aboutdialog.connect("response", self.on_aboutdialog_response)
        self.aboutdialog.connect("close", self.on_aboutdialog_close)
        self.aboutdialog.connect("delete_event", self.on_aboutdialog_close)
        self.aboutdialog.set_version(shared.VERSION)

        # set initial bottom status
        self.backbutton.hide()
        self.nextbutton.set_label('gtk-go-forward')
        self.donebutton.hide()

        # add signals
        self.tcosconfig.connect('destroy', self.exitapp )
        self.nextbutton.connect('clicked', self.on_nextbutton_click )
        self.backbutton.connect('clicked', self.on_backbutton_click )
        self.cancelbutton.connect('clicked', self.on_cancelbutton_click )
        self.donebutton.connect( 'clicked', self.on_donebutton_click )
        self.aboutbutton.connect('clicked', self.on_aboutbutton_click )
        self.startbutton.connect('clicked', self.on_startbutton_click )


        """
        http://www.pygtk.org/pygtk2tutorial-es/sec-ExpanderWidget.html
        """
        # put all expanders into a list
        self.expanders=[self.expander_debug,
                         self.expander_services,
                         self.expander_wifi,
                         self.expander_xorg, 
                         self.expander_sound,
                         self.expander_remote]
        # connect signal expanded and call on_expander_click to close others
        for exp in self.expanders:
            exp.connect('notify::expanded', self.on_expander_click)
        
        # by default all expanders closed
        for expander in self.expanders:
            #print_debug ( "closing expander %s" %(expander) )
            expander.set_expanded(False)
            
        self.settings_loaded=False

    def on_expander_click(self, expander, params):
        """
        close all expanders except actual when clicked
        """
        # exit if calling when close
        if not expander.get_expanded(): return
        for exp in self.expanders:
            if exp != expander:
                exp.set_expanded(False)

    def on_backbutton_click(self, widget):
        #print_debug ("Back clicked")
        self.changestep( -1)
        return

    def on_nextbutton_click(self, widget):
        #print_debug ("Next clicked")
        self.changestep( 1 )
        return

    def on_cancelbutton_click(self, widget):
        #print_debug ("Cancel clicked")
        self.exitapp(widget)
        return

    def on_donebutton_click(self, widget):
        #print_debug ("Done clicked")
        # 1 is for show popup
        self.saveconfig(1)
        self.exitapp(widget)
        return

    def on_aboutbutton_click(self, widget):
        #FIXME make an about window
        print_debug ("TcosGui::on_aboutbutton_click() About clicked")
        self.aboutdialog.show()
        return

    def on_aboutdialog_close(self, widget, event=None):
        print_debug ("TcosGui::on_aboutdialog_close() Closing about")
        self.aboutdialog.hide()
        return True

    def on_aboutdialog_response(self, dialog, response, *args):
        #http://www.async.com.br/faq/pygtk/index.py?req=show&file=faq10.013.htp
        if response < 0:
            dialog.hide()
            dialog.emit_stop_by_name('response')

    def on_startbutton_click(self, widget):
        #print_debug("Start clicked")
        # disable nextbutton
        self.nextbutton.set_sensitive(False)
        self.startbutton.set_sensitive(False)

        # read conf
        self.writeintoprogresstxt( _("Backup configuration settings.") )
        #backup config file
        self.backupconfig("backup")
        self.updateprogressbar(0.1)
        #time.sleep(0.3)

        self.writeintoprogresstxt( _("Overwriting it with your own settings.") )
        #FIXME save config without popup
        self.saveconfig(0)
        self.updateprogressbar(0.2)
        #time.sleep(0.3)

        # generate cmdline for gentcos
        cmdline=self.getcmdline()
        if cmdline == -1:
            # ERROR processing cmdline
            error_txt=_("Something wrong ocurred while parsing command line options for gentcos.\n\nSelect boot method??")
            self.writeintoprogresstxt( error_txt )
            self.error_msg ( error_txt )
            self.backupconfig("restore")
            return

        cmdline=shared.gentcos + cmdline
        self.writeintoprogresstxt( _("EXEC: %s\n\n") %(cmdline))

        # critical process
        gtk.gdk.threads_enter()
        self.read_exec( cmdline )
        gtk.gdk.threads_leave()

        # when done, activate nextbutton
        self.nextbutton.set_sensitive(True)


        # IMPORTANT restore backup
        self.backupconfig("restore")
        self.writeintoprogresstxt( _("Restore configuration settings.") )
        self.startbutton.set_sensitive(True)


    def read_exec(self, cmd):
        # thread function
        # Creating and starting the thread
        #print "DEBUG: creating thread with \"%s\"" %(cmd)
        ob=thread_controller( cmd, self )
        finish=True
        counter=0.2
        while finish:
            while gtk.events_pending():
                gtk.main_iteration(False)
            if ob.isfinish():
                finish=False
                self.updateprogressbar(1)
                return
            else:
                try:
                    ob.run()
                except:
                    print_debug ( "TcosGui::read_exec() Exception found" )
            self.updateprogressbar(counter)
            counter=counter+0.03
            time.sleep(0.1)


    def updateprogressbar(self, num):
        #print ("DEBUG: update progressbar to %f" %(num))
        if num > 1:
            num = 0.99
        self.gentcosprogressbar.set_fraction( num )
        if num==1:
            self.gentcosprogressbar.set_text( _("Complete") )
        return


    def backupconfig(self, method):
        # method is backup or restore
        origfile=self.tcos_config_file
        abspath = os.path.abspath(origfile)
        destfile= abspath + ".orig"
        print_debug("TcosGui::backupconfig() orig file %s" %(abspath) )
        print_debug("TcosGui::backupconfig() dest file %s" %(destfile) )
        try:
            if method == "backup":
                print_debug("TcosGui::backupconfig() Making backup...")
                shutil.copyfile(abspath, destfile)
            elif method == "restore":
                print_debug("TcosGui::backupconfig() Restoring backup...")
                shutil.copyfile(destfile, abspath)
                # re-read config file
                self.config.reset()
                self.config.getvars()
            else:
                print_debug("TcosGui::backupconfig() ERROR, unknow method %s" %(method) )
        except OSError, problem:
            print_debug("TcosGui::backupconfig() ERROR \"%s\"!!!" %(problem) )
            pass


    def saveconfig(self, popup):
        # popup boolean (show or not) info msg about vars
        print_debug ("TcosGui::saveconfig() Saving config")
        self.changedvalues=[]
        changedvaluestxt=""
        for exp in self.config.vars:
            try:
                widget=eval("self."+exp)
                #print_debug ( "TcosGui::saveconfig() widget %s found" %(exp) )
            except:
                print_debug ( "TcosGui::saveconfig() widget %s ___NOT___ found" %(exp) )
                continue
            varname = self.getvalueof_andsave(widget, exp)
            if varname != None:
                self.changedvalues.append ( varname )

        if len(self.changedvalues) > 0 and popup:
            for txt in self.changedvalues:
                changedvaluestxt+='\n' + txt
            self.info_msg( _("Configuration saved succesfully.\nChanged values are:\n %s") %(changedvaluestxt))
        return

    def getvalueof_andsave(self, widget, varname):
        wtype=[]
        widget_type=widget.class_path().split('.')
        wtype=widget_type[ len(widget_type)-1 ]
        value=str( self.config.getvalue(varname) )
        guivalue=str( self.readguiconf(widget, varname, wtype) )
        # changevalue if is distinct
        if value != guivalue:
            print_debug ("TcosGui::getvalueof() CHANGED widget=%s type=%s value=%s guiconf=%s" %(varname, wtype, value, guivalue))
            self.config.changevalue(varname, str(guivalue) )
            return( str( varname) )

    def getcmdline(self):
        """
        Generate gentcos cmdline based on tcos.conf and gui settings
        """
        # for gentcos cmdline need:
        # TCOS_KERNEL -vmlinuz
        # TCOS_METHOD -tftp -nbi -cdrom -nfs
        # TCOS_SUFFIX -suffix=foo
        # TCOS_APPEND -extra-append="foo"
        # TCOS_DEBUG -size (show ramdisk and usr.squashfs sizes)
        cmdline=""
        methodindex=self.read_select(self.TCOS_METHOD, "TCOS_METHOD")
        if methodindex == -1:
            print_debug("TcosGui::getcmdline() Unknow method in TCOS_METHOD")
            return -1
        cmdline+=" %s" %(self.search_selected_index(self.TCOS_METHOD, "TCOS_METHOD", methodindex) ) 
        
        # get TCOS_KERNEL Combobox
        model=self.TCOS_KERNEL.get_model()
        kernelindex=self.TCOS_KERNEL.get_active()
        kerneltext=model[kernelindex][0]
        print_debug("TcosGui::getcmdline() selected TCOS_KERNEL index(%d) = %s" %(kernelindex, kerneltext) )
        if kernelindex != "" and kernelindex != None and kerneltext != self.config.getvalue("TCOS_KERNEL"):
            cmdline+=" -vmlinuz=\""+ kerneltext + "\""

        # get TCOS_SUFFIX
        if self.TCOS_SUFFIX.get_text() != "" and self.TCOS_SUFFIX.get_text() != None:
            value=self.TCOS_SUFFIX.get_text()
            value=self.cleanvar(value)
            cmdline+=" -suffix=\""+ value + "\""

        is_append_in_list=False
        for item in self.changedvalues:
            if item == "TCOS_APPEND":
                is_append_in_list=True

        # get TCOS_APPEND
        if self.TCOS_APPEND.get_text() != "" and self.TCOS_APPEND.get_text() != None and is_append_in_list:
            value=self.TCOS_APPEND.get_text()
            value=self.cleanvar(value)
            cmdline+=" -extra-append=\""+ value + "\""

        # get TCOS_DEBUG
        if self.TCOS_DEBUG.get_active():
            cmdline+=" -size"

        print_debug ("getcmdline() cmdline=%s" %(cmdline) )

        return cmdline


    def populate_select(self,widget, varname):
        """
        Try to read %varname%_VALUES (in shared class) and populate ComboBox with it
        params:
            - widget = GtkComboBox to populate
            - varname = combobox name
        return:
            nothing
        """
        #print_debug ( "TcosGui::populate_select() populating \"%s\"" %(varname) )
        try:
            eval("shared."+varname+"_VALUES")
        except:
            print_debug ( "TcosGui::populate_select() WARNING: %s not have %s_VALUES, exit function..." %(varname, varname) )
            return
        
        if len(eval("shared."+varname+"_VALUES")) < 1:
            print_debug ( "TcosGui::populate_select() WARNING %s_VALUES is empty" %(varname) )
        else:
            itemlist = gtk.ListStore(str, str)
            #print eval("shared."+varname+"_VALUES")
            for item in eval("shared."+varname+"_VALUES"):
                print_debug ("TcosGui::populate_select() %s item[0]=\"%s\" item[1]=%s" %(varname, item[0], item[1]) )
                # populate select
                itemlist.append ( [item[0], item[1]] )
            widget.set_model(itemlist)
            widget.set_text_column(1)
            itemlist=None
            return

    def set_active_select(self, widget, varname, value):
        """
        Set default ComboBox value based on tcos.conf settings
        params:
            - widget = GtkComboBox to set active
            - varname = ComboBox name
            - value = value of varname in tcos.conf
        returns:
            nothing
        """
        print_debug ( "TcosGui::set_active_select() %s selected=\"%s\"" %(varname, value) )
        # search index of selected value
        try:
            values=eval("shared."+varname+"_VALUES")
        except:
            print_debug ( "TcosGui::set_active_select() WARNING: %s not have %s_VALUES" %(varname, varname) )
            return
        if len(values) < 1:
            print_debug ( "TcosGui::set_active_select() WARNING %s_VALUES is empty" %(varname) )
        else:
            for i in range(len( values ) ):
                if values[i][0] == value:
                    print_debug ( "TcosGui::set_active_selected() index=%d SELECTED=%s" %( i, values[i][0] ) )
                    widget.set_active(i)
                    return
                    

    def read_select(self, widget, varname):
        """
        Read index of active ComboBox value
        params:
            - widget = GtkComboBox to read
            - varname = ComboBox name
        return:
            index of selected value or -1 if nothing selected
        """
        print_debug ( "TcosGui::read_select() reading \"%s\"" %(varname) )
        selected=-1
        try:
            selected=widget.get_active()
        except:
            print_debug ( "TcosGui::read_select() ERROR reading %s" %(varname) )
        return selected

    def search_selected_index(self,widget,varname, index):
        """
        Convert index of selected value in tcos.conf text value
        If varname not have %varname%_VALUES return first column value
        params:
            - widget = GtkComboBox to read
            - varname = ComboBox name
            - index = index of selected value retunr by self.read.selected
        returns:
            txt value or "" if not found
        """
        value=""
        try:
            value=eval("shared.%s_VALUES[%d][0]" %(varname, index) )
            print_debug ( "TcosGui::search_selected_index() shared.%s_VALUES[%d]=%s" %(varname, index, value) )
        except:
            model=widget.get_model()
            value=model[index][0]
            print_debug ( "TcosGui::search_selected_index() unable to read %s_VALUES[%d][0], using first column \"%s\"" %(varname, index, value) )
        return value

    def cleanvar(self, value):
        # delete ;|&>< of value
        value=value.replace(' ','_') #replace spaces with _
        value=value.replace(';','_') #replace ; with _
        value=value.replace('&','_') #replace & with _
        value=value.replace('>','_') #replace > with _
        value=value.replace('<','_') #replace < with _
        value=value.replace('|','_') #replace | with _
        return value

    def readguiconf(self, widget, varname, wtype):
        value=""
        if wtype == "GtkComboBoxEntry":
            index=self.read_select(widget, varname)
            value=self.search_selected_index(widget, varname, index)
            print_debug ( "TcosGui::readguiconf() Read ComboBox %s index=%d value=%s" %(varname, index, value) )
            
        elif wtype == "GtkEntry":
            value=widget.get_text()

        elif wtype == "GtkCheckButton":
            if widget.get_active():
                value=1
            else:
                value=""

        elif wtype == "GtkSpinButton" and widget.name == "TCOS_VOLUME":
            # add % to TCOS_VOLUME
            value=str( int( widget.get_value() ) )
            value=value+"%"
        
        elif wtype == "GtkSpinButton" and widget.name != "TCOS_VOLUME":
            value=str( int( widget.get_value() ) )


        else:
            print_debug ("TcosGui::readguiconf() __ERROR__ unknow %s of type %s" %(varname, wtype) )
        return value


    def writeintoprogresstxt(self, txt):
        buffer = self.processtxt.get_buffer()
        iter = buffer.get_end_iter()
        mark = buffer.get_insert()
        txt=str(txt)
        buffer.insert(iter, '\n' + txt)
        # scroll window
        self.processtxt.scroll_to_mark(mark, 0.2)
        return


    def changestep(self, newstep):
        self.step=self.step + newstep
        if self.step <= 0:
            self.backbutton.hide()
            self.step = 0
        elif self.step == 1:
            self.backbutton.show()
            # load TCOS var settings from file and populate Gtk Entries
            self.loadsettings()

        #elif self.step == 2:
        #    self.loadsettings()
        #    # nothing to do???

        #elif self.step == 3:
        #    self.loadsettings()

        elif self.step == 4:
            self.loadsettings()
            self.nextbutton.show()
            self.donebutton.hide()

        elif self.step >= 5 : # step 5
            self.donebutton.show()
            self.nextbutton.hide()
            self.step = 5
        # move step
        if newstep == 1: # click next
            self.steps.next_page()
        else:            # click back
            self.steps.prev_page()
        return

    def loadsettings(self):
        # load defaults
        if self.settings_loaded:
            print_debug ( "TcosGui::loadsettings() Settings already loaded" )
            return

        # set default vars not in tcos.conf file
        # set default PXE build
        self.populate_select(self.TCOS_METHOD, "TCOS_METHOD")
        self.TCOS_METHOD.set_active(1)

        # set default suffix to shared vars
        import shared
        self.TCOS_SUFFIX.set_text(shared.tcos_suffix)

        # populate kernel list
        kernellist = gtk.ListStore(str)
        for kernel in self.config.kernels:
            kernellist.append([kernel.split()[0]])
        self.TCOS_KERNEL.set_model(kernellist)
        self.TCOS_KERNEL.set_text_column(0)
        #set default tcos.conf kernel
        model=self.TCOS_KERNEL.get_model()
        for i in range(len(model)):
            if model[i][0] == self.config.getvalue("TCOS_KERNEL"):
                print_debug ("TcosGui::loadsettings() TCOS_KERNEL default is %s, index %d" %( model[i][0] , i ) )
                self.TCOS_KERNEL.set_active( i )

        # read all tcos.conf and guiconf vars and populate
        for exp in self.config.vars:
            #print_debug ( "TcosGui::loadsettings() searching for %s" %(exp) )
            value=self.config.getvalue(exp)
            value=value.replace('"', '')
            if value == "":
                # empty=False, used to checkbox
                value = False

            # widget exits??
            try:
                widget=eval("self."+exp)
            except:
                print_debug ( "TcosGui::loadsettings() widget %s not found" %(exp) )
                continue

            # type of widget
            wtype=type(widget)

            if wtype == gtk.ComboBoxEntry:
                self.populate_select( widget, exp )
                self.set_active_select( widget, exp, value )

            elif wtype == gtk.Entry:
                #print_debug ( "%s is a Entry, putting value=%s" %(exp, value) )
                if value == False: value = ""
                widget.set_text(value)

            elif wtype == gtk.CheckButton:
                #print_debug ( "%s is a CheckButton" %(exp) )
                if value:
                    widget.set_active(1)
                else:
                    widget.set_active(0)

            elif wtype == gtk.SpinButton and widget.name == "TCOS_VOLUME":
                # change %
                if value.find("%") > 0:
                    # give % value
                    values=[]
                    values=value.split('%')
                    widget.set_value( float(values[0]) )
                else:
                    #give a value between 1-31, change to 1-100
                    value=float(value)*100/31
                    widget.set_value( float(value) )
            
            elif wtype == gtk.SpinButton and widget.name != "TCOS_VOLUME":
                widget.set_value( int(value) )



            else:
                print_debug( "TcosGui::loadsettings() __ERROR__ unknow %s type %s" %(exp, wtype ) )

            # put settings_loaded true to not overwrite personalized settings
            self.settings_loaded=True

    # some dialog messages
    def error_msg(self,txt):
        d = gtk.MessageDialog(None,
                          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_WARNING, gtk.BUTTONS_OK,
                          txt)
        d.run()
        d.destroy()
        print_debug ( "TcosGui::error_msg() ERROR: %s" %(txt) )


    def info_msg(self,txt):
        d = gtk.MessageDialog(None,
                          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                          txt)
        d.run()
        d.destroy()
        print_debug ( "TcosGui::info_msg() INFO: %s" %(txt) )


    def exitapp(self, widget):
        print_debug ( "TcosGui::exitapp() Exiting" )
        gtk.main_quit()
        return

    def run (self):
        gtk.main()


class thread_controller(Thread):
    # based on obex_controler
    # http://www.student.lu.se/~cif04usv/wiki/btrcv.html
    def __init__(self, cmd, gui):
        self.gui=gui
        self.finished=False
        Thread.__init__(self)
        self.p = Popen(cmd, shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT)
        self.stdout = self.p.stdout
        #print_debug ( "ThreadController::__init__() Started %s with pid %d" % (cmd, self.p.pid ) )

    def isfinish(self):
        return self.finished

    def run(self):
        while True:
            #print "THREAD: Sleeping..."
            time.sleep(0.2)
            line = self.stdout.readline()
            line = line.replace('\n', '')
            # chek if terminated
            if self.p.poll() != None:
                self.finished=True

            if line.find("DONE") > 0:
                print_debug ( "ThreadController::run() DONE found" )
            #print("THREAD: read \" %s \" " % (line) )

            while gtk.events_pending():
                gtk.main_iteration(False)

            self.gui.writeintoprogresstxt( line )
            return line




if __name__ == '__main__':
    gui = TcosGui()
    # Run app
    gtk.main()

