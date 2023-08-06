from setuptools import setup, find_packages

setup(
    name='boxv2',
    version='0.1.3.5',
    description='Box Python SDK for v2 of the Box.com API.',
    long_description="Full documentation : http://github.com/Octonius/boxv2",
    url='http://github.com/Octonius/boxv2/',
    license='MIT',
    author='octonius',
    author_email='dev@octonius.com',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['requests',],

)

#PyPI updates
#
#python setup.py sdist
#python setup.py bdist_wheel
#python setup.py register
#python setup.py sdist upload
#python setup.py sdist bdist_wheel upload
