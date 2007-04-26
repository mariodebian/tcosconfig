VERSION=0.0.3
PACKAGE=tcos-config

project=tcosconfig
project2=tcos-config

all: fix-glade es.gmo

glade:
	glade-2 $(project).glade
	make fix-glade

fix-glade:
	sh fix-glade.sh

exec:
	python $(project).py 

gedit:
	gedit-cvs tcosconfig.py Tcos*py ConfigReader.py >/dev/null 2>&1 &

clean:
	rm -f *~ *.pyc *.orig *.bak *-stamp
	if [ -d debian/tcos-config ]; then rm -rf debian/tcos-config; fi

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
	#  Creating tcos-config directories in $(DESTDIR)/
	install -d $(DESTDIR)/usr/share/$(project2)/images
	install -d $(DESTDIR)/usr/share/applications/
	install -d $(DESTDIR)/usr/share/locale/es/LC_MESSAGES/
	install -d $(DESTDIR)/usr/sbin

	# Installing tcos-config in  $(DESTDIR)
	install -m 644 $(project).glade $(DESTDIR)/usr/share/$(project2)
	install -m 644 pixmaps/tcos-icon.png $(DESTDIR)/usr/share/$(project2)/images/
	install -m 644 pixmaps/tcos-banner.png $(DESTDIR)/usr/share/$(project2)/images/
	install -m 644 images/tcos_config.png $(DESTDIR)/usr/share/$(project2)/images/
	install -m 644 tcosconfig.desktop $(DESTDIR)/usr/share/applications/


	install -m 755 tcosconfig.py $(DESTDIR)/usr/share/$(project2)/
	install -m 644 TcosGui.py $(DESTDIR)/usr/share/$(project2)/
	install -m 644 ConfigReader.py $(DESTDIR)/usr/share/$(project2)/
	install -m 644 shared.py $(DESTDIR)/usr/share/$(project2)/

	install -m 755 tcosconfig.sh $(DESTDIR)/usr/bin/tcosconfig

	# locales
	install -m 644 po/es/LC_MESSAGES/$(project).mo $(DESTDIR)/usr/share/locale/es/LC_MESSAGES/$(project).mo

uninstall:
	#  Deleting tcos_config directories
	rm -rf /usr/share/$(project2)
	rm -rf /usr/bin/tcos-config

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
	mv ../tmp ../tcos-config-$(VERSION)
	tar -czf ../tcos-config-$(VERSION).tar.gz ../tcos-config-$(VERSION)
	rm -rf ../tcos-config-$(VERSION)

tcos:
	rm -f ../tcos-config_*deb
	debuild -uc -us; true
	sudo dpkg -i ../tcos-config_*deb
