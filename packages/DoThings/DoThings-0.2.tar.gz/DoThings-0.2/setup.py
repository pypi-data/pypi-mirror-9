from setuptools import setup, find_packages

setup(
    name='DoThings',
    version='0.2',
    url='https://github.com/marzinz/things/',
    license='BSD',
    author='Marzin Zhu',
    author_email='marzin.zhu@gmail.com',
    description='Simple To-Do-List in Termial',
    packages=find_packages(),
    install_requires=['docopt'],
    entry_points={
            'console_scripts':['things = things:main'],
    }
)