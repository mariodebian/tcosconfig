LANGUAGES=es pt_BR ca@valencia fr gl qcv

all: gmo


clean:
	@echo " **CLEAN**"
	@rm -rf *.mo *~ tmp/
	@for lang in $(LANGUAGES); do \
		echo " **CLEANDIR** $$lang"; \
		rm -rf $$lang;\
	done

files:
	find ../ -name "*.py" -o -name "*.ui" > FILES
pot:
#	xgettext  -o tcosconfig.pot --files-from=FILES
	find ../ -name "*.ui" > FILES.ui.txt
	find ../ -name "*.py" > FILES.py.txt
	xgettext -o tcosconfig.py.pot --files-from=FILES.py.txt --language=Python
	xgettext -o tcosconfig.ui.pot --files-from=FILES.ui.txt --language=Glade
	msgcat -o tcosconfig.pot tcosconfig.py.pot tcosconfig.ui.pot
	rm -f tcosconfig.py.pot tcosconfig.ui.pot FILES.ui.txt FILES.py.txt

po:
	@for lang in $(LANGUAGES); do \
		echo " **PO** $$lang"; \
		if [ ! -f $$lang.po ]; then \
			msginit --input tcosconfig.pot -o $$lang-old.po;\
		else \
			mv $$lang.po $$lang-old.po; \
		fi ; \
		msgmerge -o $$lang.po $$lang-old.po tcosconfig.pot; \
		rm -f $$lang-old.po; \
	done

gmo:
	@echo " **COMPILING** languages: $(LANGUAGES)"
	@for lang in $(LANGUAGES); do \
		echo " **COMPILEMO** $$lang" ; \
		mkdir -p $$lang/LC_MESSAGES/; \
		msgfmt --verbose -o $$lang/LC_MESSAGES/tcosconfig.mo $$lang.po; \
	done
	
install:
	@echo " **INSTALL** languages: $(LANGUAGES)"
	@for lang in $(LANGUAGES); do \
		echo " **INSTALLMO** $$lang" ; \
		mkdir -p $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/; \
		msgfmt -o $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/tcosconfig.mo $$lang.po; \
	done
	
