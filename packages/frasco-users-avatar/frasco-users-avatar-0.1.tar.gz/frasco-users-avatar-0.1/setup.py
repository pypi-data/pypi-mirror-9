from setuptools import setup


setup(
    name='frasco-users-avatar',
    version='0.1',
    url='http://github.com/frascoweb/frasco-users-avatar',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Avatars for Frasco-Users",
    py_modules=['frasco_users_avatar'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'frasco-users'
    ]
)