from distutils.core import setup, Command


class Tox(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call('tox')
        raise SystemExit(errno)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('VERSION') as version_file:
    version = version_file.read().rstrip()

setup(
    name="fastpay",
    packages=['fastpay'],
    version=version,
    author="yahoowallet",
    author_email="fastpay-help@mail.yahoo.co.jp",
    url="https://fastpay.yahoo.co.jp",
    description="fastpay sdk for python",
    long_description=readme,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP"
    ],
    license='MIT',
    cmdclass={'test': Tox},
    test_require=['tox'],
    install_requires=[
        'requests>=2.2.1'
    ]
)
