from setuptools import setup

setup(name='pypybox',
      version='0.1',
      description='Boxes in your CLI',
      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          # How mature is this project? Common values are
          # 3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Utilities',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ],

      url='http://github.com/JustB/pybox',
      author='Giustino Borzacchiello',
      author_email='giustinob@gmail.com',
      license='MIT',
      packages=['pybox'],
      zip_safe=False,
      install_requires=['docopt'],
      entry_points={
          'console_scripts': [
              'pypybox=pybox.pybox:main',
          ],
      })
