from setuptools import setup, find_packages

setup( 
    name = 'hitboxy', 
    description = 'Wrapper around the Hitbox API',
    version = '0.1.3',
    author = 'David Ewelt', 
    author_email = 'uranoxyd@gmail.com',
    url = 'https://bitbucket.org/Uranoxyd/hitboxy',
    license = 'BSD',
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        
        'Intended Audience :: Developers',        
        'Topic :: Software Development :: Libraries :: Python Modules',
        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords = 'hitbox hitbox.tv api'
)