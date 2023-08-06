from setuptools import setup, find_packages

setup(
    name = "Sqlchemyforms",
    version = '1.0',
    description = "Generate form objects for create HTML forms based on SQLAlchhemy models",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/sqlchemyforms',
    license = 'MIT',
    install_requires = [
        "SQLAlchemy >= 0.9.8",
    ],
    packages = find_packages(),
)

