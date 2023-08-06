from setuptools import setup, Extension, find_packages

setup(name='yaul',
      version='0.4.3',
      author='Filip Sufitchi',
      author_email="fsufitchi@gmail.com",
      description="Yet Another Utility Library",
      url="https://github.com/fsufitch/YAUL",
      packages=['yaul'],
      package_dir={'':'src'},
      entry_points = {
        },

      install_requires=['contextlib2', 'python-daemon', 'psutil'],
      )
