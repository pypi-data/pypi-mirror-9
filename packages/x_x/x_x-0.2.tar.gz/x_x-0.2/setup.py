from setuptools import setup

setup(
    name='x_x',
    author='Kristian Perkins',
    author_email='khperkins@gmail.com',
    version='0.2',
    url='http://github.com/krockode/x_x',
    py_modules=['x_x'],
    description='Excel file CLI Reader',
    long_description=open('README.rst').read(),
    license='Apache 2.0',
    packages= [
        'x_x',
    ],
    package_dir={'requests': 'requests'},
    install_requires=[
        'xlrd',
        'click',
    ],
    entry_points='''
       [console_scripts]
        x_x=x_x.x_x:cli
    ''',
    classifiers=(
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
    ),
)
