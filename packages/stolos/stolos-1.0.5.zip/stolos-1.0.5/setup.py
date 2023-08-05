try:
    from distutils.core import setup  # , Extension
    from setuptools import find_packages, findall
except ImportError:
    print ("Please install Distutils and setuptools"
           " before installing this package")
    raise

setup(
    name='stolos',
    version='1.0.5',
    description=(
        'A DAG-based job queueing system and executor for performing work'
        ' with complex dependency requirements between applications'),
    long_description="Check the project homepage for details",
    keywords=[
        'stolos', 'scheduler', 'dag', 'directed acyclic graph', 'graph',
        'data', 'dependency', 'queue', 'queueing system', 'pipeline',
        'applications', 'machine learning', 'executor'],

    author='Sailthru Data Science Team',
    author_email='agaudio@sailthru.com',
    url='https://github.com/sailthru/stolos',

    packages=find_packages(),
    scripts=['./bin/stolos-submit'],
    data_files=[
        ('conf', findall('conf')),
        ('stolos/examples', findall('stolos/examples'))
    ],

    install_requires = [
        'kazoo>=1.3.1',
        'networkx>=1.8.1',
        'ujson>=1.33',
        'argparse>=1.1',
        'pygraphviz>=1.2',
        'argparse_tools>=1.0.0',
    ],

    extras_require={
        'pyspark': ['pyspark'],
        'redis': ['redis', 'hiredis'],
        'testing': [
            'nose>=1.3.3', 'colorlog>=2.2.0', 'pyflakes>=0.8.1',
            'pep8>=1.5.6'],
    },

    # include_package_data = True,
    zip_safe = False,

    # Include code that isn't pure python (like c stuff)
    # ext_modules=[Extension('foo', ['foo.c'])]

    entry_points = {
        'console_scripts': [
            'stolos = stolos.__main__:go',
        ],
        'setuptools.installation': [
            'eggsecutable = stolos.__main__:go',
        ],
    },
)
