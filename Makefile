all: fix-glade

include common.mk

glade:
	glade-2 $(project).glade
	make fix-glade

fix-glade:
	bash fix-glade.sh

exec:
	python $(project).py --debug

gedit:
	gedit-cvs tcosconfig.py Tcos*py ConfigReader.py >/dev/null 2>&1 &

clean:
	rm -f *~ *.pyc *.orig *.bak *-stamp *glade.backup
	rm -rf pixmaps/
	cd po && make clean
	dh_clean

pot:
	cd po && make pot

es.po:
	############################################################
	#   OBSOLETE Makefile target => cd po and make into it     #
	############################################################
	@exit 1

es.gmo: es.po


install:
	#  Creating tcosconfig directories in $(DESTDIR)/
	install -d $(DESTDIR)/usr/share/$(project)/images
	install -d $(DESTDIR)/usr/share/applications/
	install -d $(DESTDIR)/usr/share/locale/es/LC_MESSAGES/
	install -d $(DESTDIR)/usr/bin

	# Installing tcosconfig in  $(DESTDIR)
	install -m 644 $(project).glade $(DESTDIR)/usr/share/$(project)
	install -m 644 images/tcos-icon.png $(DESTDIR)/usr/share/$(project)/images/
	install -m 644 images/tcos-banner.png $(DESTDIR)/usr/share/$(project)/images/
	install -m 644 images/tcos_config.png $(DESTDIR)/usr/share/$(project)/images/
	install -m 644 tcosconfig.desktop $(DESTDIR)/usr/share/applications/


	install -m 755 tcosconfig.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 TcosGui.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 ConfigReader.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 shared.py $(DESTDIR)/usr/share/$(project)/

	install -m 644 TcosChrootBuilder.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 DetectArch.py $(DESTDIR)/usr/share/$(project)/
#	install -m 644 VirtualTerminal.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 tcos-chrootbuilder.glade $(DESTDIR)/usr/share/$(project)/

	install -m 755 tcosconfig.sh $(DESTDIR)/usr/bin/tcosconfig

	# locales
	cd po && make install DESTDIR=$(DESTDIR)

uninstall:
	#  Deleting tcos_config directories
	rm -rf /usr/share/$(project)
	rm -rf /usr/bin/tcosconfig

	#locales
	rm /usr/share/locale/es/LC_MESSAGES/$(project).mo


targz:
	rm -rf ../tmp 2> /dev/null
	mkdir ../tmp
	cp -ra * ../tmp
	###################
	# Borrando svn... #
	###################
	rm -rf `find ../tmp/* -type d -name .svn`
	mv ../tmp ../tcosconfig-$(VERSION)
	tar -czf ../tcosconfig-$(VERSION).tar.gz ../tcosconfig-$(VERSION)
	rm -rf ../tcosconfig-$(VERSION)

tcos:
	rm -f ../tcosconfig_*deb
	debuild -uc -us; true
	sudo dpkg -i ../tcosconfig_*deb


patch_version:
	# obsolete target patch_version



patch_hardy:
	echo 6 > debian/compat
	sed -i 's/7\.0\.0/6\.0\.0/g' debian/control
	sed -i 's/3\.8\.0/3\.7\.2/g' debian/control

patch_intrepid:
	# nothing to patch

patch_jaunty:
	# nothing to patch

patch_max:
	# nothing to patch


patch_lenny:
	# nothing to patch

patch_testing:
	# nothing to patch

patch_unstable:
	# nothing to patch


