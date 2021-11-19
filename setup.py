from setuptools import find_packages, setup

setup(
    name='tbfo',
    version='1.0.0',
    author='MARS without the M',
    author_email='13520103@std.stei.itb.ac.id',
    description=''.join([
        'Python Grammar Parser',
    ]),
    url='https://github.com/rifqi2320/Python-Grammar-Checker',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
)