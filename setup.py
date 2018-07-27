from setuptools import setup

setup(
    name='savant_get',
    version='0.0.1',
    description='Go get all that data from Baseball Savant',
    author='Jared Martin',
    author_email='jared.martin@mlb.com',
    py_modules=['savant_get'],
    entry_points={'console_scripts': ['savant-get=savant_get:main']},
    python_requires='>=3.4',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
