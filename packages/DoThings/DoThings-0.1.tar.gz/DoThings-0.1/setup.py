from setuptools import setup

setup(
    name='DoThings',
    version='0.1',
    url='https://github.com/marzinz/dothings/',
    license='BSD',
    author='Marzin Zhu',
    author_email='marzin.zhu@gmail.com',
    description='Simple To-Do-List in Termial',
    install_requires=['docopt'],
    entry_points={
            'console_scripts':[
                'things=things.main',
            ],
    }
)
