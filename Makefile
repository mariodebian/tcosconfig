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
	install -m 644 VirtualTerminal.py $(DESTDIR)/usr/share/$(project)/
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
	# PATCHING VERSION
	sed -i 's/__VERSION__/$(VERSION)/g' shared.py
	sed -i 's/__VERSION__/$(VERSION)/g' tcosconfig.py
	sed -i 's/__VERSION__/$(VERSION)/g' TcosGui.py
	sed -i 's/__VERSION__/$(VERSION)/g' ConfigReader.py
	sed -i 's/__VERSION__/$(VERSION)/g' DetectArch.py
	sed -i 's/__VERSION__/$(VERSION)/g' TcosChrootBuilder.py
	sed -i 's/__VERSION__/$(VERSION)/g' VirtualTerminal.py

patch_dapper: patch_version
	# PATCHING TcosConfig in Ubuntu DAPPER
	sed -i '/^Build/s/5.0.37.2/5.0.7ubuntu13/g' debian/control
	sed -i '/python-support/s/0.3/0.1.1ubuntu1/g' debian/control
	sed -i '/dh_pysupport/s/dh_pysupport/dh_python/g' debian/rules
	sed -i '/PYTHON/s/python/python2.4/g' tcosconfig.sh


patch_edgy: patch_version
	# nothing to patch

patch_feisty: patch_version
	# nothing to patch

patch_gutsy: patch_version
	# nothing to patch

patch_hardy: patch_version
	# nothing to patch

patch_max: patch_version
	# nothing to patch

patch_etch: patch_version
	# nothing to patch

patch_testing: patch_version
	# nothing to patch

patch_unstable: patch_version
	# nothing to patch


