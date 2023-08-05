from distutils.core import setup

setup(
    name='package-install-check',
    version='1.0',
    author='Fernando de Alcantara Correia',
    author_email='fernandoacorreia@gmail.com',
    packages=['PackageInstallCheck'],
    scripts=[],
    url='https://github.com/fernandoacorreia/package-install-check',
    license='MIT',
    description='Checks if Python package installation worked.',
    long_description='A dummy package meant to be used in integration tests to check if automated Python package installation is working.'
)
