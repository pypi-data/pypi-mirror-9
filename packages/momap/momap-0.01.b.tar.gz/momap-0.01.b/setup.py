from distutils.core import setup

setup(
    name='momap',
    version='0.01.b',
    packages=['momap'],

    install_requires=['sortedcontainers'],
    platforms='any',

    author='Zhenbo Li',
    author_email='litimetal@gmail.com',
    license='MIT',
    url='https://github.com/Endle/momap',

    description='Multi Ordered Map for python',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ]
)
