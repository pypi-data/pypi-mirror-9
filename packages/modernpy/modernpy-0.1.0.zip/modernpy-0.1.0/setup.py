from setuptools import setup, find_packages

version = '0.1.0'

packages = find_packages()

setup(
    name='modernpy',
    version=version,
    description='Extension methods for built-in type in Python.',
    author='Shinz Natkid',
    author_email='shinznatkid@gmail.com',
    url='https://github.com/shinznatkid/modernpy',
    packages=find_packages(),
    install_requires=[
        'forbiddenfruit',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
