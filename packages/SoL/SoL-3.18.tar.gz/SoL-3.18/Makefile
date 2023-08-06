#-*- coding: utf-8 -*-
#:Progetto:  SoL
#:Creato:    sab 08 nov 2008 21:16:39 CET
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

export TOPDIR := $(CURDIR)
PYTHON := $(BINDIR)python
SOLSRC := $(TOPDIR)/src/sol
SOLADMIN := $(BINDIR)soladmin
ALEMBIC = $(BINDIR)alembic -n app:main -c development.ini

.PHONY: clean
clean:
	$(MAKE) -C docs clean
	rm -rf build $(SOLSRC)/static/manual
	rm -f $(PACKED_CSS) $(PACKED_JS)
	-@find docs src -name '*~' -print0 | xargs -r0 rm

.PHONY: distclean
distclean: clean
	rm -f development.db

development.db:
	$(SOLADMIN) initialize-db development.ini
	$(SOLADMIN) restore development.ini

.PHONY: generate-db-migration
generate-db-migration:
	read -p "Enter migration description: " MDESC && \
	  $(ALEMBIC) revision --autogenerate -m "$$MDESC"

.PHONY: upgrade-db
upgrade-db:
	$(SOLADMIN) upgrade-db development.ini

.PHONY: serve
serve: development.db
	pserve development.ini

.PHONY: test
test:
	@$(PYTHON) setup.py nosetests

include Makefile.i18n
include Makefile.manual
include Makefile.release
