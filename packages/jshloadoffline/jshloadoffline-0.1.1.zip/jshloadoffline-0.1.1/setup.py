"""
jshloadoffline
----------------

Load offline prefetched data in JSH
"""
from setuptools import setup

setup(
    name='jshloadoffline',
    version='0.1.1',
    url='https://github.com/lixxu/jshloadoffline',
    license='BSD',
    author='Lix Xu',
    author_email='xuzenglin@gmail.com',
    description='Load offline prefetched data in JSH',
    long_description=__doc__,
    packages=['jshloadoffline'],
    zip_safe=False,
    platforms='any',
    install_requires=['path.py'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
