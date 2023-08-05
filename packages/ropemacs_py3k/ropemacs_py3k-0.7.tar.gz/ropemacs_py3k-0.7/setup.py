extra_kwargs = {}
try:
    from setuptools import setup
    extra_kwargs['install_requires'] = ['rope_py3k >= 0.9.4',
                                        'ropemode_py3k']
except ImportError:
    from distutils.core import setup


classifiers = [
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Environment :: X11 Applications',
    'Environment :: Win32 (MS Windows)',
    'Environment :: MacOS X',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Topic :: Text Editors :: Emacs',
    'Topic :: Software Development']


def get_long_description():
    lines = open('README.rst').read().splitlines(False)
    end = lines.index('Setting Up')
    return '\n' + '\n'.join(lines[:end]) + '\n'

setup(name='ropemacs_py3k',
      version='0.7',
      description='An emacs mode for using rope python refactoring library for Python3',  # noqa
      long_description=get_long_description(),
      packages=['ropemacs'],
      author='Atila Neves',
      author_email='atila.neves@gmail.com',
      url='https://github.com/atilaneves/ropemacs',
      license='GNU GPL',
      classifiers=classifiers,
      requires=['ropemode_py3k'],
      **extra_kwargs)
