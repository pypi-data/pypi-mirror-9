from setuptools import setup, find_packages

setup(
    name = 'plutonium-plugin-output-transmission',
    version = '1.0.1',
    description = 'Transmission output plugin for Plutonium',
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/plutonium-plugin-output-transmission',
    license = 'MIT',
    install_requires = [
        'plutonium == 1.0',
        'transmissionrpc == 0.11',
    ],
    include_package_data = True,
    packages = find_packages(),
)
