from setuptools import setup

setup(name='git2mine',
      version='0.2',
      description=("A python application aimed to make easier the tedious task of logging time for Redmine tasks"
                   " by extracting information from GIT commits comments"),
      url='http://github.com/pfcoperez/git2mine',
      author='Pablo Francisco Perez Hidalgo',
      author_email='contact@pablofranciscoperez.info',
      license='GPLV2',
      packages=['git2mine'],
      install_requires=[
        'PyGTK',
        'GitPython',
        'pyredmine'
      ],
      scripts = [
        'bin/mineCommits.py'
      ],
      include_package_data=True,
      zip_safe=False)