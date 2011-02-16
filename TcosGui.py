# -*- coding: UTF-8 -*-
#    TcosConfig version __VERSION__
#
# Copyright (c) 2006-2011 Mario Izquierdo <mariodebian@gmail.com>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from ConfigReader import ConfigReader
import shared

from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import os
import shutil
#import sys, re
import pygtk
pygtk.require('2.0')
import gtk
import time
from gettext import gettext as _
from gettext import locale

import pwd
import sys

#gtk.threads_init()
gtk.gdk.threads_init()


def print_debug(txt):
    global debug
    if shared.debug:
        print( "%s::%s " %(__name__, txt) )

class TcosGui:
    def __init__(self):
        import shared
        self.isfinished=False
        self.changedvalues=[]
        # load some classes
        self.tcos_config_file = shared.tcos_config_file

        if pwd.getpwuid(os.getuid())[0] != "root":
            self.error_msg( _("Error, you must run this app as root user") )
            sys.exit(1)

        self.config=ConfigReader()
        
        self.step=0

        self.languages=[locale.getdefaultlocale()[0]]
        if self.languages[0] and "_" in self.languages[0]:
            self.languages.append( self.languages[0].split('_')[0] )
            self.languages.append( self.languages[0].split('_')[1] )
        print_debug ( "__init__ languages=%s" %self.languages)

        # Widgets
        print_debug ("loading %s"%(shared.UI_DIR + 'tcosconfig.ui'))
        self.ui = gtk.Builder()
        self.ui.set_translation_domain(shared.PACKAGE)
        print_debug("Loading ui file...")
        self.ui.add_from_file(shared.UI_DIR + 'tcosconfig.ui')
        
        # load all widgets
        for widget in self.ui.get_objects():
            if hasattr(widget, 'get_name'):
                setattr(self, widget.get_name(), widget)

        for widget in self.ui.get_objects():
            try:
                if issubclass(type(widget), gtk.Buildable):
                    name = gtk.Buildable.get_name(widget)
                    setattr(self, name, widget)
                    #print_debug("widget_name %s" %name)
            except AttributeError, err:
                print "Exception get_objects() err=%s"%err


        self.steps.set_show_tabs(False)
        
        self.tcosconfig.set_icon_from_file(shared.IMG_DIR +'tcos-icon.png')

        self.aboutui=gtk.Builder()
        self.aboutui.set_translation_domain(shared.PACKAGE)
        self.aboutui.add_from_file(shared.UI_DIR + 'tcosconfig-aboutdialog.ui')
        
        self.aboutdialog = self.aboutui.get_object("aboutdialog")
        self.aboutdialog.connect("response", self.on_aboutdialog_response)
        self.aboutdialog.connect("close", self.on_aboutdialog_close)
        self.aboutdialog.connect("delete_event", self.on_aboutdialog_close)
        self.aboutdialog.set_version(shared.VERSION)
        self.aboutdialog.set_name('TcosConfig')
        self.aboutdialog.set_icon_from_file(shared.IMG_DIR +'tcos-icon.png')

        # set initial bottom status
        self.backbutton.hide()
        self.nextbutton.set_label('gtk-go-forward')
        self.donebutton.hide()

        # add signals
        self.tcosconfig.connect('destroy', self.on_cancelbutton_click )
        self.nextbutton.connect('clicked', self.on_nextbutton_click )
        self.backbutton.connect('clicked', self.on_backbutton_click )
        self.cancelbutton.connect('clicked', self.on_cancelbutton_click )
        self.donebutton.connect( 'clicked', self.on_donebutton_click )
        self.aboutbutton.connect('clicked', self.on_aboutbutton_click )
        self.startbutton.connect('clicked', self.on_startbutton_click )


        self.TCOS_TEMPLATE.connect('changed', self.on_template_change)

        """
        http://www.pygtk.org/pygtk2tutorial-es/sec-ExpanderWidget.html
        """
        # put all expanders into a list
        self.expanders=[self.expander_debug,
                         self.expander_services,
                         self.expander_wifi,
                         self.expander_xorg, 
                         self.expander_dri, 
                         self.expander_sound,
                         self.expander_remote,
                         self.expander_auth, 
                         self.expander_bootmenu,
                         self.expander_kernel, # expand by default kernel
                         self.expander_thinclients, 
                         self.expander_other ]
        # connect signal expanded and call on_expander_click to close others
        for exp in self.expanders:
            exp.connect('notify::expanded', self.on_expander_click)
        
        # by default all expanders closed
        for expander in self.expanders:
            #print_debug ( "closing expander %s" %(expander) )
            expander.set_expanded(False)
            
        self.settings_loaded=False
        
        for radio in ["TCOS_MENU_MODE", "TCOS_MENU_MODE_SIMPLE", "TCOS_MENU_MODE_GRAPHIC"]:
            widget=getattr(self, radio)
            widget.connect('toggled', self.on_tcos_menu_mode_change)
        self.menu_type=""
        
        if len(shared.TCOS_PLYMOUTH_VALUES) == 1 and shared.TCOS_PLYMOUTH_VALUES[0][0]=="":
            self.TCOS_DISABLE_PLYMOUTH.set_active(True)
            self.TCOS_PLYMOUTH.set_sensitive(False)
            self.TCOS_DISABLE_PLYMOUTH.set_sensitive(False)
            self.hbox_plymouth.hide()
        if len(shared.TCOS_USPLASH_VALUES) == 1 and shared.TCOS_USPLASH_VALUES[0][0]=="":
            self.TCOS_DISABLE_USPLASH.set_active(True)
            self.TCOS_USPLASH.set_sensitive(False)
            self.TCOS_DISABLE_USPLASH.set_sensitive(False)
            self.hbox_usplash.hide()
        #self.TCOS_XORG_DRI.connect('toggled', self.on_disable_dri_change)
        self.TCOS_DISABLE_USPLASH.connect('toggled', self.on_disable_usplash_change)
        self.TCOS_DISABLE_PLYMOUTH.connect('toggled', self.on_disable_plymouth_change)


        # events for linked widgets
        for widget in shared.linked_widgets:
            if not hasattr(self, widget): continue
            w=getattr(self, widget)
            data=shared.linked_widgets[widget]
            w.connect(data[0], self.on_linked_widgets, data)

    def on_linked_widgets(self, widget, data):
        active=widget.get_active()
        if active:
            other=data[1]
        else:
            other=data[2]
        if len(other) < 1:
            #print_debug("on_linked_widgets() nothing to do")
            return
        for w in other:
            if hasattr(self, w):
                wid=getattr(self, w)
                enabled=wid.get_active()
                if other[w] != None:
                    wid.set_active(other[w])
                    wid.set_sensitive(other[w])
                    #print dir(getattr(self, w))
                    if hasattr(wid, "set_tooltip_markup"):
                        wid.set_tooltip_markup( _("Need to enable <b>%s</b> before") %(gtk.Buildable.get_name(widget)) )
                else:
                    wid.set_sensitive(True)
                    if hasattr(wid, "set_tooltip_text"):
                        wid.set_tooltip_text( "" )
                #print_debug("on_linked_widgets() widget=%s enabled=%s new=%s"%(w, enabled, other[w]) )
                
    def on_disable_plymouth_change(self, widget):
        print_debug("on_disable_plymouth_change() value=%s"%widget.get_active())
        if widget.get_active():
            self.TCOS_PLYMOUTH.set_sensitive(False)
        else:
            self.TCOS_PLYMOUTH.set_sensitive(True)
            
    def on_disable_usplash_change(self, widget):
        print_debug("on_disable_usplash_change() value=%s"%widget.get_active())
        if widget.get_active():
            self.TCOS_USPLASH.set_sensitive(False)
        else:
            self.TCOS_USPLASH.set_sensitive(True)
            
    def on_disable_dri_change(self, widget):
        print_debug("on_disable_dri_change() value=%s"%widget.get_active())
        if widget.get_active():
            self.TCOS_XORG_DRI_RADEON.set_sensitive(True)
        else:
            self.TCOS_XORG_DRI_RADEON.set_sensitive(False)

    def on_tcos_menu_mode_change(self, widget):
        #print_debug("on_tcos_menu_mode_change() widget=%s active=%s"%(widget.name, widget.get_active()))
        if not widget.get_active():
            return
        menu_type=gtk.Buildable.get_name(widget).replace('TCOS_MENU_MODE','').replace('_','')
        print_debug("on_tcos_menu_mode_change() widget=%s type=%s" %(gtk.Buildable.get_name(widget),menu_type))
        for item in shared.TCOS_MENUS_TYPES:
            #print_debug("on_tcos_menu_mode_change() item[0]=%s menu_type=%s"%(item[0], menu_type))
            if item[0] == menu_type:
                self.config.changevalue("TCOS_NETBOOT_MENU", item[1])
                self.config.changevalue("TCOS_NETBOOT_MENU_VESA", item[2])
                self.TCOS_NETBOOT_HIDE_INSTALL.set_sensitive(item[3])
                self.TCOS_NETBOOT_HIDE_LOCAL.set_sensitive(item[4])

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
        self.config.revert()
        return

    def on_donebutton_click(self, widget):
        #print_debug ("Done clicked")
        # 1 is for show popup
        #self.saveconfig(True)
        self.exitapp(widget)
        return

    def on_aboutbutton_click(self, widget):
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
        textbuffer = self.processtxt.get_buffer()
        textbuffer.set_text('')
        if self.TCOS_ROOT_PASSWD.get_text() == "" and self.config.use_secrets == False:
            self.info_msg(_("You leave blank root password for thin clients in:\n    - Advanced settings -> Users and passwords\
                            \n\nThe password will be established to: \"root\""))
        #print_debug("Start clicked")
        # disable nextbutton
        self.nextbutton.set_sensitive(False)
        self.startbutton.set_sensitive(False)
        self.backbutton.set_sensitive(False)
        self.cancelbutton.set_sensitive(False)


        # read conf
        #self.writeintoprogresstxt( _("Backup configuration settings.") )
        #backup config file
        #self.backupconfig("backup")
        #self.updateprogressbar(0.1)
        #time.sleep(0.3)

        self.writeintoprogresstxt( _("Overwriting it with your own settings.") )
        #FIXME save config without popup
        self.saveconfig(False)
        self.updateprogressbar(0.05)
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
        self.writeintoprogresstxt( _("EXEC: %s") %(cmdline))

        # start generate in a thread
        th=Thread(target=self.generateimages, args=(cmdline,) )
        th.start()
        

    def enablebuttons(self):
        # when done, activate nextbutton
        self.nextbutton.set_sensitive(True)
        self.backbutton.set_sensitive(True)
        self.cancelbutton.set_sensitive(True)

        # IMPORTANT restore backup
        #self.backupconfig("restore")
        #self.writeintoprogresstxt( _("Restore configuration settings.") )
        self.startbutton.set_sensitive(True)

    
    def generateimages(self, cmdline):
        self.isfinished=False
        p = Popen(cmdline, shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT, close_fds=True)
        print_debug ("generateimages() exec: %s"%cmdline)
        stdout=p.stdout
        counter=0.1
        step=0.02
        while not self.isfinished:
            time.sleep(0.1)
            line=stdout.readline().replace('\n','')
            
            if len(line) > 0:
                counter=counter+step
                
            if p.poll() != None:
                self.isfinished=True
            
            if 'bash: no job' in line or \
               'root@' in line or \
               'df: Warning' in line:
                print_debug("generateimages() NO VISIBLE LINE %s"%line)
                continue
            
            print_debug("generateimages() %s"%line)
            gtk.gdk.threads_enter()
            self.updateprogressbar(counter)
            self.writeintoprogresstxt( line )
            gtk.gdk.threads_leave()
        
        gtk.gdk.threads_enter()
        self.enablebuttons()
        self.updateprogressbar(1)
        gtk.gdk.threads_leave()

    
    def updateprogressbar(self, num):
        #print ("DEBUG: update progressbar to %f" %(num))
        if num > 1:
            num = 0.99
        self.gentcosprogressbar.set_fraction( num )
        self.gentcosprogressbar.set_text( _("Working... (%d %%)") %int(num*100) )
        if num==1:
            self.gentcosprogressbar.set_text( _("Complete") )
        return


    def backupconfig(self, method):
        return
        # method is backup or restore
        origfile=self.tcos_config_file
        abspath = os.path.abspath(origfile)
        destfile= abspath + ".orig"
        print_debug("TcosGui::backupconfig() orig file %s" %(abspath) )
        print_debug("TcosGui::backupconfig() dest file %s" %(destfile) )
        if shared.debug:
            os.system("diff -ur %s %s" %(abspath, destfile) )
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
        print_debug ("saveconfig() Saving config")
        
        changedvaluestxt=''
        active_menu=''
        # get value of TCOS_NETBOOT_MENU
        for w in ['TCOS_MENU_MODE', 'TCOS_MENU_MODE_SIMPLE', 'TCOS_MENU_MODE_GRAPHIC']:
            if getattr(self, w).get_active():
                active_menu=w.replace('TCOS_MENU_MODE', '').replace('_','')
        
        for menu in shared.TCOS_MENUS_TYPES:
            if active_menu == menu[0]:
                print_debug("saveconfig() menu=%s self.config.menus=%s" %(menu, self.config.menus) )
                
        print_debug("saveconfig() ACTIVE MENU =%s"%active_menu)
        
        for exp in self.config.confdata:
            if not hasattr(self, exp):
                if exp in ["TCOS_NETBOOT_MENU", "TCOS_NETBOOT_MENU_VESA"]:
                    self.changedvalues.append ( exp )
                #print_debug ( "saveconfig() widget %s ___NOT___ found" %(exp) )
                continue
            widget=getattr(self, exp)
            
            varname = self.getvalueof_andsave(widget, exp)
            #print_debug ("saveconfig() exp=%s varname=%s"%(exp, varname))
            if varname != None:
                self.changedvalues.append ( varname )
                
        print_debug("saveconfig() changedvalues=%s"%self.changedvalues)
        if len(self.changedvalues) > 0:
            self.config.savedata(self.changedvalues)
            
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
        #print_debug("getvalueof_andsave() varname=%s, oldvalue=%s guivalue=%s wtype=%s ##################" %(varname, value, guivalue, wtype) )
        # changevalue if is distinct
        if value != guivalue:
            print_debug ("getvalueof() CHANGED widget=%s type=%s value=%s guiconf=%s" %(varname, wtype, value, guivalue))
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

        is_append_in_list=False
        for item in self.changedvalues:
            if item == "TCOS_APPEND":
                is_append_in_list=True

        # get TCOS_APPEND
        if self.TCOS_APPEND.get_text() != "" and self.TCOS_APPEND.get_text() != None and is_append_in_list:
            value=self.TCOS_APPEND.get_text()
            value=self.cleanvar(value, spaces=False)
            cmdline+=" -extra-append=\""+ value + "\""

        # get TCOS_DEBUG
        if self.TCOS_DEBUG.get_active():
            cmdline+=" -size"

        print_debug ("getcmdline() cmdline=%s" %(cmdline) )
        if shared.updatetcosimages:
            # return cmdline into ""
            return "--gentcos=\"%s\"" %(cmdline)
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
        if not hasattr(shared, varname+"_VALUES"):
            #print_debug ( "TcosGui::populate_select() WARNING: %s not have %s_VALUES" %(varname, varname) )
            return
        values=getattr(shared, varname+"_VALUES")
        
        
        if len(values) < 1:
            print_debug ( "TcosGui::populate_select() WARNING %s_VALUES is empty" %(varname) )
        else:
            itemlist = gtk.ListStore(str, str)
            #print eval("shared."+varname+"_VALUES")
            for item in values:
                #print_debug ("TcosGui::populate_select() %s item[0]=\"%s\" item[1]=%s" %(varname, item[0], item[1]) )
                # populate select
                itemlist.append ( [item[0], item[1]] )
            widget.set_model(itemlist)
            if widget.get_text_column() != 1:
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
        # search index of selected value
        if not hasattr(shared, varname+"_VALUES"):
            #print_debug ( "TcosGui::set_active_select() WARNING: %s not have %s_VALUES" %(varname, varname) )
            return
        values=getattr(shared, varname+"_VALUES")
        
        if len(values) < 1:
            print_debug ( "TcosGui::set_active_select() WARNING %s_VALUES is empty" %(varname) )
        else:
            for i in range(len( values ) ):
                if values[i][0] == value:
                    #print_debug ( "TcosGui::set_active_selected() index=%d SELECTED=%s" %( i, values[i][0] ) )
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
        #print_debug ( "TcosGui::read_select() reading \"%s\"" %(varname) )
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
        print_debug("search_selected_index widget=%s varname=%s index=%s"%(widget,varname, index))
        value=""
        # if index is < 0 return empty string (PLYMOUTH_DISABLE)
        if index < 0:
            return ''
        if hasattr(shared, varname + "_VALUES"):
            return getattr(shared, varname + "_VALUES")[index][0]
        
        model=widget.get_model()
        if varname == "TCOS_TEMPLATE":
            return model[index][1]
        else:
            return model[index][0]
        

    def cleanvar(self, value, spaces=True):
        # delete ;|&>< of value
        if spaces:
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
            #print_debug ( "TcosGui::readguiconf() Read ComboBox %s index=%d value=%s" %(varname, index, value) )
            
        elif wtype == "GtkEntry":
            value=widget.get_text()

        elif wtype == "GtkCheckButton":
            if widget.get_active():
                value=1
            else:
                value=""

        elif wtype == "GtkSpinButton" and gtk.Buildable.get_name(widget) == "TCOS_VOLUME":
            # add % to TCOS_VOLUME
            value=str( int( widget.get_value() ) )
            value=value+"%"
        
        elif wtype == "GtkSpinButton" and gtk.Buildable.get_name(widget) != "TCOS_VOLUME":
            value=str( int( widget.get_value() ) )
        
        elif wtype == "GtkSpinButton" and gtk.Buildable.get_name(widget) != "TCOS_MAX_MEM":
            value=str( int( widget.get_value() ) )
        elif wtype == "GtkSpinButton" and gtk.Buildable.get_name(widget) != "TCOS_COMPCACHE_PERCENT":
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
        #print_debug("changestep() newstep=%s"%newstep)
        self.step=self.step + newstep
        if self.step <= 0:
            self.backbutton.hide()
            self.step = 0
        elif self.step == 1:
            print_debug("changestep() ****** STEP 1 ****")
            self.backbutton.show()
            if newstep == 1:
                self.config.loadbase()
                self.config.loadtemplates()
                self.populatetemplates()
            # load TCOS var settings from file and populate Gtk Entries
            #self.loadsettings()

        #elif self.step == 2:
        #    self.loadsettings()
        #    # nothing to do???

        #elif self.step == 3:
        #    self.loadsettings()

        elif self.step == 6:
            self.nextbutton.show()
            self.donebutton.hide()

        elif self.step >= 7 : # step 5
            self.donebutton.show()
            self.nextbutton.hide()
            self.step = 7
        # move step
        if newstep == 1: # click next
            self.steps.next_page()
        else:            # click back
            self.steps.prev_page()
        return

    def on_template_change(self, widget):
        self.changedvalues=[]
        model=widget.get_model()
        value=model[widget.get_active()][1]
        if value:
            print_debug("****** ON_TEMPLATE_CHANGE() ***** value=%s"%value)
            self.config.reloadtemplate(value)
            self.loadsettings()
            self.config.changevalue("TCOS_TEMPLATE", value)

    def getTranslatedDescription(self, tpl):
        for lang in self.languages:
            if self.config.templates[tpl].has_key('TEMPLATE_DESCRIPTION_' +  lang):
                return self.config.templates[tpl]['TEMPLATE_DESCRIPTION_' + lang]
        
        if self.config.templates[tpl].has_key('TEMPLATE_DESCRIPTION'):
            return self.config.templates[tpl]['TEMPLATE_DESCRIPTION']
        
        return _("No template description avalaible")

    def populatetemplates(self):
        default_template=self.config.getvalue('TCOS_TEMPLATE')
        if os.path.exists(shared.tcosconfig_template):
            default_template=os.path.basename(shared.tcosconfig_template)
        elif os.path.exists(shared.tcos_force_base_template):
            default_template=os.path.basename(shared.tcos_force_base_template)
        print_debug("populatetemplates() default=%s"%default_template)
        # populate template list
        templatelist = gtk.ListStore(str,str)
        templatelist.append( [ "base.conf : " + _("don't use any template") , "base.conf"] )
        i=0
        for tpl in self.config.templates:
            text="%s : %s" %(tpl, self.getTranslatedDescription(tpl))
            if tpl == default_template:
                default_template=i
                print_debug("populatetemplates() default_template tpl=%s i=%s"%(tpl, i))
            templatelist.append([text,tpl])
            i+=1
        self.TCOS_TEMPLATE.set_model(templatelist)
        if self.TCOS_TEMPLATE.get_text_column() != 0:
            self.TCOS_TEMPLATE.set_text_column(0)
        self.TCOS_TEMPLATE.set_active(default_template+1) # set i+1 because base.conf is 0
        
    def loadsettings(self):
        # set default PXE build
        self.populate_select(self.TCOS_METHOD, "TCOS_METHOD")
        self.TCOS_METHOD.set_active(1)

        # configure boot menu
        #("TCOS_NETBOOT_MENU", item[1])
        #("TCOS_NETBOOT_MENU_VESA", item[2])
        default_menu=False
        for item in shared.TCOS_MENUS_TYPES:
            if self.config.getvalue('TCOS_NETBOOT_MENU') == item[1] and self.config.getvalue('TCOS_NETBOOT_MENU_VESA') == item[2]:
                # set menu type to item[0]
                if item[0] == '':
                    widget=self.TCOS_MENU_MODE
                    default_menu=True
                else:
                    widget=getattr(self, 'TCOS_MENU_MODE' + '_' + item[0])
                print_debug("loadsettings() TCOS_MENU_MODE=%s"%gtk.Buildable.get_name(widget))
                widget.set_active(True)
                print_debug("loadsettings() NETBOOT_HIDE_INSTALL = %s"%item[3])
                
        if default_menu:
            print_debug("loadsettings() default menu disable hide_install and hide_local")
            self.TCOS_NETBOOT_HIDE_INSTALL.set_sensitive(False)
            self.TCOS_NETBOOT_HIDE_LOCAL.set_sensitive(False)
        

        # overwrite method (tcos.conf.nfs use it)
        if self.config.getvalue('TCOS_METHOD') != '':
            model=self.TCOS_METHOD.get_model()
            for i in range(len(model)):
                if model[i][0] == self.config.getvalue('TCOS_METHOD'):
                    self.TCOS_METHOD.set_active(i)

        # populate kernel list
        kernellist = gtk.ListStore(str)
        for kernel in self.config.kernels:
            kernellist.append([kernel.split()[0]])
        self.TCOS_KERNEL.set_model(kernellist)
        if self.TCOS_KERNEL.get_text_column() != 0:
            self.TCOS_KERNEL.set_text_column(0)
        #set default tcos.conf kernel
        model=self.TCOS_KERNEL.get_model()
        for i in range(len(model)):
            print_debug ("TcosGui::loadsettings() TCOS_KERNEL model[i][0] is '%s' default '%s' KERNEL_FIXED is '%s'" 
                          %(model[i][0], self.config.getvalue("TCOS_KERNEL"), self.config.getvalue("TCOS_KERNEL_FIXED")) )
            if self.config.getvalue("TCOS_KERNEL_FIXED") != "":
                if model[i][0] == self.config.getvalue("TCOS_KERNEL_FIXED"):
                    print_debug ("TcosGui::loadsettings() TCOS_KERNEL default is %s, index %d" %( model[i][0] , i ) )
                    self.TCOS_KERNEL.set_active( i )
            elif model[i][0] == self.config.getvalue("TCOS_KERNEL"):
                print_debug ("TcosGui::loadsettings() TCOS_KERNEL default is %s, index %d" %( model[i][0] , i ) )
                self.TCOS_KERNEL.set_active( i )

        # read all tcos.conf and guiconf vars and populate
        for exp in self.config.confdata:
            #print_debug ( "TcosGui::loadsettings() searching for %s" %(exp) )
            value=self.config.confdata[exp]
            value=value.replace('"', '')
            if value == "":
                # empty=False, used to checkbox
                value = False

            # widget exits??
            if hasattr(self, exp):
                widget=getattr(self, exp)
            else:
                if not exp in self.config.ignored_widgets:
                    print_debug("loadsettings() widget %s don't exists"%exp)
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

            elif wtype == gtk.SpinButton and gtk.Buildable.get_name(widget) == "TCOS_VOLUME":
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
            
            elif wtype == gtk.SpinButton and gtk.Buildable.get_name(widget) != "TCOS_VOLUME":
                #print widget
                #print gtk.Buildable.get_name(widget)
                widget.set_value( int(value) )
            
            elif wtype == gtk.SpinButton and gtk.Buildable.get_name(widget) != "TCOS_MAX_MEM":
                widget.set_value( int(value) )
            elif wtype == gtk.SpinButton and gtk.Buildable.get_name(widget) != "TCOS_COMPCACHE_PERCENT":
                widget.set_value( int(value) )
            
            else:
                print_debug( "TcosGui::loadsettings() __ERROR__ unknow %s type %s" %(exp, wtype ) )
        
        if os.path.isfile(shared.config_file_secrets):
            try:
                fd=file(shared.config_file_secrets, 'r')
            except:
                return
            data=fd.readline()
            fd.close()
            if data != "\n":
                self.config.use_secrets=True
                self.TCOS_ADMIN_USER.set_text("")
                self.TCOS_ROOT_PASSWD.set_text("")
                self.TCOS_ADMIN_USER.set_sensitive(False)
                self.TCOS_ROOT_PASSWD.set_sensitive(False)
                
            
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
        self.isfinished=True
        gtk.main_quit()
        return

    def run (self):
        gtk.main()




if __name__ == '__main__':
    gui = TcosGui()
    # Run app
    gtk.main()

