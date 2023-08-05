from setuptools import setup

setup(
    name='aiqterminal',
    version='0.1',
    description='Interactive shell for administrating a AIQ8 platform server',
    author='Erik Lundberg',
    author_email='lundbergerik@gmail.com',
    py_modules=['aiqterminal'],
    install_requires=[
        'aiqpy',
        'click'
    ],
    keywords=['aiq8', 'appeariq'],
    zip_safe=False,
    entry_points='''
        [console_scripts]
        aiqterminal=aiqterminal:main
    '''
)
