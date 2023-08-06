from setuptools.command.install import install
from setuptools import setup, find_packages
import projectkey
import codecs
import sys
import os


def read(*parts):
    # intentionally *not* adding an encoding option to open
    # see here: https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts), 'r').read()

class ArgumentCompletionInstall(install):
    """Install arg completion if projectkey is installed using system python."""
    def run(self):
        install.run(self)
        if sys.executable.startswith("/usr"):
            os.system("activate-global-python-argcomplete")

setup(name="projectkey",
      version=projectkey.__version__,
      description="A tool for running a suite of custom project commands invoked via one key.",
      long_description=read('README.rst'),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Build Tools',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
#          'Programming Language :: Python :: 3',
#          'Programming Language :: Python :: 3.1',
#          'Programming Language :: Python :: 3.2',
#          'Programming Language :: Python :: 3.3',
      ],
      keywords='development environment tool automation project',
      author='Colm O\'Connor',
      author_email='colm.oconnor.github@gmail.com',
      url='https://github.com/crdoconnor/projectkey',
      license='MIT',
      install_requires=['argcomplete>=0.8.1'],
      packages=find_packages(exclude=[]),
      package_data={},
      entry_points=dict(console_scripts=['k=projectkey:k_runner.k_runner', ]),
      zip_safe=False,
      cmdclass={'install': ArgumentCompletionInstall},
)
