from distutils.core import setup

# also update in urlnorm.py
version = '1.1.3'

setup(name='urlnorm',
        version=version,
        long_description=open("./README.txt", "r").read(),
        description="Normalize a URL to a standard unicode encoding",
        py_modules=['urlnorm'],
        license='MIT License',
        author='Jehiah Czebotar',
        author_email='jehiah@gmail.com',
        url='http://github.com/jehiah/urlnorm',
        )
