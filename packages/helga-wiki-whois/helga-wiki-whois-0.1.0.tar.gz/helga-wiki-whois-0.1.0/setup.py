from setuptools import setup, find_packages

setup(
    name='helga-wiki-whois',
    version='0.1.0',
    description='A helga command to generate confluence-type URLs for users',
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
    keywords='helga wiki whois',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-wiki-whois",
    packages=find_packages(),
    py_modules=['helga_wiki_whois'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'wiki_whois = helga_wiki_whois:wiki_whois',
        ],
    ),
)
