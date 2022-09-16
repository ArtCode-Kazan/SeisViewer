VERSION=2.2.1

python_version_full := $(wordlist 2,4,$(subst ., ,$(shell python3 --version 2>&1)))
python_version_major := $(word 1,${python_version_full})
python_version_minor := $(word 2,${python_version_full})
python_version_patch := $(word 3,${python_version_full})


install-python:
	sudo apt-get update
	sudo apt-get -y upgrade
	sudo apt install -y software-properties-common gcc wget unzip
	sudo apt autoremove -y

	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt install -y python3.8 python3.8-dev python3.8-distutils

	wget https://bootstrap.pypa.io/get-pip.py
	sudo python3.8 get-pip.py
	sudo python3.8 -m pip install --upgrade pip


install-dependencies:
	python3.8 -m pip install pyQt5 pyqtgraph

	wget https://github.com/MikkoArtik/SeisCore/archive/refs/heads/main.zip
	unzip main.zip -d seiscore-package
	cd seiscore-package/SeisCore-main && make package-install
	rm -rf main.zip seiscore-package


install:
ifeq (${python_version_major}, 3)
ifeq (${python_version_minor}, 8)
	@echo "Python version 3.8 installed"
else
	make install-python
endif
else
	make install-python
endif

	sudo make install-dependencies
	python3.8 setup.py bdist_wheel
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seisviewer-$(VERSION)-py3-none-any.whl

	python3.8 alias_install.py
	$(shell source ~/.bashrc)
