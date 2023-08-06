import distutils.core

version = '0.1'

distutils.core.setup(
        name='i-pylogger',
        version=version,
        packages=['pylogger'],
        author='Justin',
        author_email='justinli.ljt@gmail.com',
        url='https://github.com/jizhouli/py-logger',
        license='http://opensource.org/licenses/MIT',
        description='a easy-to-use logging wrapper for Python'
        )
