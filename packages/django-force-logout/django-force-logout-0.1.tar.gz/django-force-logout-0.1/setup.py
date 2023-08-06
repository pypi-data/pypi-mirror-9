from distutils.core import setup

setup(
    name='django-force-logout',
    version='0.1',
    packages=(
        'django_force_logout',
    ),
    install_requires = ['django'],
    description="Django Force Logout",
    author="Chris Lamb",
    author_email="chris@chris-lamb.co.uk",
    url="https://github.com/thread/django-force-logout",
    download_url="https://github.com/thread/django-force-logout/archive/master.zip"
)
