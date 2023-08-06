from distutils.core import setup

setup(name='kineticlib',
      version='1.2.2',
      description='Library for kinetic theory calculations in the multi-temperature and state-to-state approximations',
      author='George Oblapenko',
      author_email='kunstmord@kunstmord.com',
      url='https://github.com/Kunstmord/kineticlib',
      license="MIT",
      packages=['kineticlib'],
      package_dir={'kineticlib': 'src/kineticlib'},
      package_data={'kineticlib': ['data/models/*.csv', 'data/particles/*.dat', 'data/spectra/*.dat']},
      requires=['numpy', 'scipy'],
      include_package_data=True,
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        ],
      long_description = """\
      KineticLib
      ==========

      Provides a library with various functions used in computational kinetic theory.
      Aimed at the multi-temperature (and one-temperature as a special case) and state-to-state approximations.

      Documentation is available here: http://kineticlib.readthedocs.org/en/latest/

      For changes see CHANGELOG.rst (https://github.com/Kunstmord/kineticlib/blob/master/CHANGELOG.rst)


      Roadmap (major additions)
      =========================

      `List of planned additions to Kineticlib <https://github.com/Kunstmord/kineticlib/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement>`_

      Current issues
      ==============

      `List of Kineticlib issues <https://github.com/Kunstmord/kineticlib/issues?q=is%3Aopen+is%3Aissue+label%3Abug>`_
      """
      )