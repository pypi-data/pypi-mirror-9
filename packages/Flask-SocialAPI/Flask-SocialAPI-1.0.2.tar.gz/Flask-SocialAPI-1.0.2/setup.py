from setuptools import setup

setup(
    name="Flask-SocialAPI",
    version="1.0.2",
    url="https://github.com/leejaedus/Flask-SocialAPI",
    author='Lee Jae Yeon',
    author_email='leejaeduss@gmail.com',
    description='Simple api for controlling and login to provider',
    packages=[
        'flask_socialapi',
        'flask_socialapi.providers'
    ],
    install_requires=[
        'Flask-OAuthlib'
    ],
    tests_require=[
        'Flask',
        'Flask-Login'
    ],
    zip_safe=False
)