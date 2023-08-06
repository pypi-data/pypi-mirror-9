from distutils.core import setup

setup(
    name='IVisual',
    version='0.1.92',
    author='John Coady',
    author_email='johncoady@shaw.ca',
    packages=['ivisual', 'ivisual.test'],
    package_data={'ivisual': ['data/*.js']},
    url='http://pypi.python.org/pypi/IVisual/',
    license='LICENSE.txt',
    description='VPython visual inline for IPython Notebook',
    long_description=open('README.txt').read(),
    classifiers=[
          'Framework :: IPython',
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Natural Language :: English',
          'Programming Language :: Python :: 2.7',
          'Topic :: Multimedia :: Graphics :: 3D Modeling',
          'Topic :: Multimedia :: Graphics :: 3D Rendering',
          'Topic :: Scientific/Engineering :: Visualization',
    ],
)