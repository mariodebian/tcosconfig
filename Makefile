all: fix-glade

include common.mk

glade:
	glade-3 ui/$(project).ui

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







tcos:
	rm -f ../tcosconfig_*deb
	debuild -uc -us; true
	sudo dpkg -i ../tcosconfig_*deb



patch_hardy:
	echo 6 > debian/compat
	sed -i 's/7\.0\.0/6\.0\.0/g' debian/control
	sed -i 's/3\.8\.0/3\.7\.2/g' debian/control
