from setuptools import setup, find_packages

setup(
    name='AuthZ-Group',
    version='1.1.4',
    description='Group interface and implementations',
    install_requires=['Django'],
    packages=find_packages(exclude=["project"]),
    include_package_data=True,  # use MANIFEST.in during install
    author = "Patrick Michaud",
    author_email = "pmichaud@uw.edu",
    license = "Apache 2.0",
    keywords = "django groups authorization",
    url = "https://github.com/vegitron/authz_group/"
)
