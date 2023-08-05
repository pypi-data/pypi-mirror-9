from pip.req import parse_requirements
import setuptools

with open('README.rst') as f:
    readme = f.read()

with open('HISTORY.rst') as f:
    history = f.read()

setuptools.setup(name='Flask-XStatic',
                 version='0.0.1',
                 author='Etienne Millon',
                 author_email='me@emillon.org',
                 url="https://github.com/emillon/flask-xstatic",
                 license='BSD',
                 py_modules=['flask_xstatic'],
                 install_requires=[
                     'Flask',
                     'XStatic',
                     ],
                 zip_safe=False,
                 description='Flask support for XStatic assets',
                 long_description=readme + '\n\n' + history,
                 test_suite='nose.collector',
                 classifiers=[
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.3',
                     'Topic :: Internet :: WWW/HTTP',
                     ],
                 )
