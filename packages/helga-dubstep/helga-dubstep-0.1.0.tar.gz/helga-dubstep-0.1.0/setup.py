from setuptools import setup, find_packages

setup(
    name='helga-dubstep',
    version='0.1.0',
    description=("A match plugin that will respond with vaiable length 'wubwubwub' when "
                 "someone mentions the word 'dubstep'."),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Framework :: Twisted',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='helga dubstep',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-dubstep",
    packages=find_packages(),
    py_modules=['helga_dubstep'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'dubstep = helga_dubstep:dubstep',
        ],
    ),
)
