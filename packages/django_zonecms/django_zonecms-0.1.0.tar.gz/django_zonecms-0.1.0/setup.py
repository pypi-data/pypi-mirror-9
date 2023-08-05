from setuptools import setup, find_packages

packages = ['Django']

setup(
    name="django_zonecms",
    version="0.1.0",
    url="http://github.com/argaen/django_zonecms",
    description="Minimal cms for single page websites with dynamic content.",
    author="argaen",
    author_email="manu.mirandad@gmail.com",
    include_package_data=True,
    packages=find_packages(exclude=['examples',]),
    keywords=['django', 'cms', 'dynamic', 'single page'],
    install_requires=['Django>=1.7', 'django-filer', 'django-mptt', 'easy_thumbnails', 'django-polymorphic' ]
)
