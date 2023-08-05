from setuptools import setup, find_packages

setup(
    name="spouk_utils",
    version="0.1",
    packages=find_packages(),

    # metadata for upload to PyPI
    author="spouk",
    author_email="spouk@spouk.ru",
    description="some utils for flask distributions",
    license="PSF",
    keywords="spouk-utils, flask utils",
    url="",  # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
    install_requires=['hashlib', 'flask', 'BeautifulSoup', 'Pillow', 'email']
)