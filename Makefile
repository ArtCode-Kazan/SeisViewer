VERSION=2.2.9


install-dependencies:
	wget https://github.com/ArtCode-Kazan/SeisCore/archive/refs/heads/main.zip
	unzip main.zip -d seiscore-package
	cd seiscore-package/SeisCore-main && make install
	sudo rm -rf main.zip seiscore-package
	sudo poetry install --no-root


update-dependencies:
	wget https://github.com/ArtCode-Kazan/SeisCore/archive/refs/heads/main.zip
	unzip main.zip -d seiscore-package
	cd seiscore-package/SeisCore-main && make update
	sudo rm -rf main.zip seiscore-package


create-build:
	python3.8 setup.py bdist_wheel
	rm -rf build && rm -rf seisviewer.egg-info


install:
	make install-dependencies
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seisviewer-$(VERSION)-py3-none-any.whl

	python3.8 aliases.py --install
	$(shell source ~/.bashrc)


uninstall:
	sudo python3.8 -m pip uninstall -y seisviewer

	python3.8 aliases.py --remove
	$(shell source ~/.bashrc)


update:
	make uninstall
	make update-dependencies
	make create-build
	cd $(CURDIR)/dist && sudo python3.8 -m pip install seisviewer-$(VERSION)-py3-none-any.whl

	python3.8 aliases.py --install
	$(shell source ~/.bashrc)
