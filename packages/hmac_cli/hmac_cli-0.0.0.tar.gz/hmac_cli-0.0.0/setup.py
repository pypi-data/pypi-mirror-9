import os
from setuptools import setup

this_dir = os.path.dirname(__file__)
long_description = "\n" + open(os.path.join(this_dir, 'README.rst')).read()

setup(
    name='hmac_cli',
    version='0.0.0',
    description='Simple CLI for encrypting data with a private key, using HMAC',
    long_description=long_description,
    keywords='hmac',
    author='Marc Abramowitz',
    author_email='msabramo@gmail.com',
    url='https://github.com/msabramo/hmac_cli',
    py_modules=['hmac_cli'],
    zip_safe=False,
    install_requires=['click'],
    entry_points="""\
      [console_scripts]
      hmac = hmac_cli:cli
    """,
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
)
