from setuptools import setup

setup(
    name='framework-puithon',
    version='0.1.2',
    description='A framework for easy gluing HTML based frontend with Python backend, for desktop-based applications.',
    packages=['example', 'puithon'],
    license='',
    author='Grayson Wen',
    author_email='wenoptics@gmail.com',
    url='https://github.com/wenoptics/PuiTHON',
    include_package_data=True,
    install_requires=[
        'cefpython3',
    ],
)
