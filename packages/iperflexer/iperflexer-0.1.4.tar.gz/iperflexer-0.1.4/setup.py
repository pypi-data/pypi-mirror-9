from distutils.command.sdist import sdist
import os

try:
    from setuptools import setup, find_packages
except ImportError as error:
    from distribute_setup import use_setuptools
    use_setuptools()

# put the readme in for pypi
with open('readme.rst') as reader:
    long_description = reader.read()

# from the Hitchhiker's Guide to Python
# http://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/specification.html
class sdist_hg(sdist):
    user_options = sdist.user_options + [
        ('dev', None, "Add a dev marker")
        ]

    def initialize_options(self):
        sdist.initialize_options(self)
        self.dev = 0

    def run(self):
        if self.dev:
            suffix = '.dev%d' % self.get_tip_revision()
            self.distribution.metadata.version += suffix
            sdist.run(self)
            
    def get_tip_revision(self, path=os.getcwd()):
        from mercurial.hg import repository
        from mercurial.ui import ui
        from mercurial import node
        repo = repository(ui(), path)
        tip = repo.changelog.tip()
        return repo.changelog.rev(tip)

#      cmdclass = {'sdist':sdist_hg},    
setup(name='iperflexer',
      version="0.1.4",

      description="A program to parse iperf files",
      long_description=long_description,
      author="russell",
      platforms=['linux'],
      url = 'https://bitbucket.org/cloisteredmonkey-admin/iperflexer',
      author_email="necromuralist@gmail.com",
      license = "MIT",
      packages = find_packages(exclude=['tests*']),
      include_package_data = True,
      package_data = {"":["*.rst", "*.ini"]},
      entry_points = """
	  [console_scripts]
      parseiperf=iperflexer.main:main
	  """
      )
#      
#      install_requires = ['pudb', 'mock'],
# an example last line would be cpm= cpm.main: main

# If you want to require other packages add (to setup parameters):
# install_requires = [<package>],
#version=datetime.today().strftime("%Y.%m.%d"),
# if you have an egg somewhere other than PyPi that needs to be installed as a dependency, point to a page where you can download it:
# dependency_links = ["http://<url>"]
