from setuptools import setup, find_packages

setup(
    name = "plutonium-plugin-configui-web",
    version = '1.0',
    description = "Web based config user interface plugin for Plutonium",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/plutonium-plugin-configui-web',
    license = 'MIT',
    install_requires = [
        'plutonium == 1.0',
        'sqlchemyforms == 1.0',
    ],
    include_package_data = True,
    packages = find_packages(),
)
