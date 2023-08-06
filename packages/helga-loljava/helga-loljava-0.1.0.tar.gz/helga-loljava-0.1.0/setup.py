from setuptools import setup, find_packages


setup(
    name='helga-loljava',
    version='0.1.0',
    description=("A helga plugin that will respond with a silly generated Java class name "
                 "when someone mentions the word 'java'."),
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
    keywords='helga loljava java',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-loljava",
    packages=find_packages(),
    py_modules=['helga_loljava'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'loljava = helga_loljava:make_bullshit_java_thing',
        ],
    ),
)
