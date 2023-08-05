from setuptools import setup, find_packages

install_requires=['requests', 'docopt']

try:
    import json
except ImportError:
    install_requires.append('simplejson')

setup(
    name='gist_it',
    version='1.0.5',
    license='MIT',
    description='Gist_it can send gist',
    author='se s',
    url='https://github.com/gk024kfd/gist_it',
    author_email='3f2j3g02jgw@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            'gist_it = main.main:main'
    },
    zip_safe=False,
    classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
    ],
)
