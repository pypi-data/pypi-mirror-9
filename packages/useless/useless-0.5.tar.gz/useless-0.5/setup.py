from setuptools import setup, find_packages


setup(
    name="useless",
    version='0.5',
    author='Riccardo Cagnasso',
    author_email="riccardo@phascode.org",
    description='Useless is useless. Oh yeah, and parses bit and pieces' +
                'of ELF and PE dynamic libraries',
    license="MIT",
    packages=find_packages('src'),
    package_dir={'useless': 'src/useless/',
                 'useless.elf': 'src/useless/elf/'},

    scripts=['src/usls.py'],
    install_requires=[
        'cached_property',
        'prettytable'],
    keyword="ELF PE PortableExecutable",
    url="https://github.com/riccardocagnasso/python-opendb/blob/master/setup.py")
