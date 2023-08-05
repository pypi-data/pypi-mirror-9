from setuptools import setup, find_packages

setup(
    name='emencia-recipe-drdump',
    version=__import__('emencia_recipe_drdump').__version__,
    description=__import__('emencia_recipe_drdump').__doc__,
    long_description=open('README.rst').read(),
    author='David Thenon',
    author_email='dthenon@emencia.com',
    url='https://github.com/emencia/emencia-recipe-drdump',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'zc.buildout',
        'zc.recipe.egg',
        'dr-dump>=0.2.3',
    ],
    entry_points={
        'zc.buildout': [
            'default = emencia_recipe_drdump.recipe_interface:DrDumpRecipe',
        ]
    },
    include_package_data=True,
    zip_safe=False
)
