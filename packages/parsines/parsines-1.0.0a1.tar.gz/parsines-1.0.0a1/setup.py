from setuptools import setup

setup(name="parsines",
      version="1.0.0a1",
      description="A library for reading iNES formatted NES ROM files.",
      long_description="A library for reading iNES formatted NES ROM files. Includes a CLI utility for querying files directly",
      url="https://www.github.com/wkmanire/ines",
      author="wkmanire",
      author_email="williamkmanire@gmail.com",
      license="GPLv3",
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: System :: Emulators',
          'Topic :: Utilities',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4'
      ],
      keywords="nes emulation ines rom",
      packages=["parsines"],
      entry_points={'console_scripts': [
              'ines-util=parsines.cli:main',
          ]
      }
)
