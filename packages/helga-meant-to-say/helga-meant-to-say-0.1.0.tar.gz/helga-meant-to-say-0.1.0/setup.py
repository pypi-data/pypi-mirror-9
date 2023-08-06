from setuptools import setup, find_packages


setup(
    name='helga-meant-to-say',
    version='0.1.0',
    description="A helga plugin that lets users correct what they said, like using s/foo/bar",
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
    keywords='helga meant-to-say sed',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-meant-to-say",
    packages=find_packages(),
    py_modules=['helga_meant_to_say'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'meant_to_say = helga_meant_to_say:meant_to_say',
        ],
    ),
)
