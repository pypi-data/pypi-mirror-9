from distutils.core import setup

setup(
    name='decipher',
    version='28.00.4',
    description="Package for easier access to FocusVision's Decipher REST API",
    author='Erwin S. Andreasen',
    long_description=open('README.rst').read(),
    author_email='beacon-api@decipherinc.com',
    url='http://ww2.focusvision.com/products/decipher',
    packages=['decipher', 'decipher.commands'],
    license="BSD",
    requires=["requests"],
    scripts=['scripts/beacon']
)
