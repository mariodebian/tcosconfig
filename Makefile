all: fix-glade es.gmo

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
	rm -f *~ *.pyc *.orig *.bak *-stamp
	rm -rf po/es
	dh_clean

pot:
	xgettext -o po/tcosconfig.pot --files-from=po/FILES

es.po:
	rm -f po/$(project).glade.pot
	msginit --input po/$(project).pot -o po/es-new.po
	msgmerge -o po/es-new.po po/es.po po/$(project).pot
	##################################################
	#           translate po/es-new.po               #
	##################################################

es.gmo:
	if [ -f po/es-new.po ]; then  mv po/es-new.po po/es.po ; fi
	mkdir -p po/es/LC_MESSAGES/
	msgfmt -o po/es/LC_MESSAGES/$(project).mo po/es.po


install:
	#  Creating tcosconfig directories in $(DESTDIR)/
	install -d $(DESTDIR)/usr/share/$(project)/images
	install -d $(DESTDIR)/usr/share/applications/
	install -d $(DESTDIR)/usr/share/locale/es/LC_MESSAGES/
	install -d $(DESTDIR)/usr/bin

	# Installing tcosconfig in  $(DESTDIR)
	install -m 644 $(project).glade $(DESTDIR)/usr/share/$(project)
	install -m 644 pixmaps/tcos-icon.png $(DESTDIR)/usr/share/$(project)/images/
	install -m 644 pixmaps/tcos-banner.png $(DESTDIR)/usr/share/$(project)/images/
	install -m 644 images/tcos_config.png $(DESTDIR)/usr/share/$(project)/images/
	install -m 644 tcosconfig.desktop $(DESTDIR)/usr/share/applications/


	install -m 755 tcosconfig.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 TcosGui.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 ConfigReader.py $(DESTDIR)/usr/share/$(project)/
	install -m 644 shared.py $(DESTDIR)/usr/share/$(project)/

	install -m 755 tcosconfig.sh $(DESTDIR)/usr/bin/tcosconfig

	# locales
	install -m 644 po/es/LC_MESSAGES/$(project).mo $(DESTDIR)/usr/share/locale/es/LC_MESSAGES/$(project).mo

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

patch_dapper: patch_version
	# PATCHING TcosConfig in Ubuntu DAPPER
	sed -i '/^Build/s/5.0.37.2/5.0.7ubuntu13/g' debian/control
	sed -i '/python-support/s/0.3/0.1.1ubuntu1/g' debian/control
	sed -i '/dh_pysupport/s/dh_pysupport/dh_python/g' debian/rules


patch_edgy: patch_version
	# nothing to patch

patch_feisty: patch_version
	# nothing to patch

patch_etch: patch_version
	# nothing to patch

patch_unstable: patch_version
	# nothing to patch


