from setuptools import setup, find_packages

setup( 
    name = 'hitboxy', 
    description = 'Wrapper around the Hitbox API',
    long_description = "Hitboxy is small Python wrapper around the Hitbox API. Its written in pure python.\n\nFor feedback, bug reports or feature proposals please use the Bitbucket repository https://bitbucket.org/Uranoxyd/hitboxy/overview",
    version = '0.1.8',
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
        'Programming Language :: Python :: 3',
    ],
    keywords = 'hitbox hitbox.tv api'
)