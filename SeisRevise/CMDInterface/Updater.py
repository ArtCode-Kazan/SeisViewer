import urllib.request as r

from pip._internal import main as pipmain


def read_version_file():
    version_file = 'https://github.com/MikkoArtik/Distr/raw/dev/SeisRevise/' \
                   'version.txt'
    result = dict()
    f = r.urlopen(version_file)
    for line in f:
        line = line.strip().decode('ascii')
        line = line.split('=')
        result[line[0]] = line[1]
    return result


def update_python_packs():
    seis_core_pack = 'https://github.com/MikkoArtik/Distr/raw/dev/SeisRevise' \
                     '/Python/SeisCore.egg'
    seis_revise_pack = 'https://github.com/MikkoArtik/Distr/raw/dev/SeisRevise' \
                       '/Python/SeisRevise.egg'
    pipmain(['install', seis_core_pack])


update_python_packs()
