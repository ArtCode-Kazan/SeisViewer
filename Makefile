VERSION=2.2.3

python_version_full := $(wordlist 2,4,$(subst ., ,$(shell python3 --version 2>&1)))
python_version_major := $(word 1,${python_version_full})
python_version_minor := $(word 2,${python_version_full})
python_version_patch := $(word 3,${python_version_full})


install-dependencies:
	sudo python3.8 -m pip install pyQt5 pyqtgraph==0.12.1

	wget https://github.com/MikkoArtik/SeisCore/archive/refs/heads/main.zip
	unzip main.zip -d seiscore-package
	cd seiscore-package/SeisCore-main && make install
	sudo rm -rf main.zip seiscore-package


after-build:
	rm -rf build && rm -rf seisviewer.egg-info


create-build:
	python3.8 setup.py bdist_wheel
	make after-build


install:
	make install-dependencies
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seisviewer-$(VERSION)-py3-none-any.whl

	python3.8 aliases.py --install
	$(shell source ~/.bashrc)
	history -c


uninstall:
	sudo python3.8 -m pip uninstall seisviewer

	python3.8 aliases.py --remove
	$(shell source ~/.bashrc)
	history -c


update:
	make uninstall
	make install-dependencies
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seisviewer-$(VERSION)-py3-none-any.whl

	python3.8 aliases.py --install
	$(shell source ~/.bashrc)
	history -c
