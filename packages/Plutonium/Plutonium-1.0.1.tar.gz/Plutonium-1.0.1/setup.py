from setuptools import setup, find_packages

setup(
    name = "Plutonium",
    version = '1.0.1',
    description = "RSS fetcher for bittorrent feeds",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/plutonium',
    license = 'MIT',   
    install_requires = [
        "SQLAlchemy >= 0.9.8",
        "alembic == 0.7.4",
        "python-jsonrpc == 0.6.1",
        "Unidecode == 0.04.17",
    ],
    packages = find_packages(),
    include_package_data = True,
    scripts = [
        'bin/plutonium',
        'bin/plutonium_starter',
    ],
)
