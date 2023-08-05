from distutils.core import setup

__docformat__ = 'restructuredtext'

setup(
    name='pym',
    packages=['pym'],
    version='0.1.2',
    description='Console based paged menu module',
    author='Mike Bond',
    author_email='mikeb@hitachi-id.com',
    url='https://bitbucket.org/mbondfusion/pym',
    download_url='https://bitbucket.org/mbondfusion/pym/get/v0.1.2.tar.gz',
    keywords=['console', 'menu', 'paging'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Software Development :: Libraries'
    ],
    license='GNU General Public License v3 (GPLv3)',
    requires=['colorama (>=0.3.2)', 'ansicolors (>=1.0.2)'],
    long_description="""Summary:
=========

The pym module is a console based menu system for Python 3.x+. It outputs provided menu choices with pagination depending on your current terminal size.


Example:
========

.. sourcecode:: python

    from pym.menu import Menu

    choices = {
        'option1': 'First Option',
        'option2': 'Second Option',
        'option3': 'Third Option',
        'option4': 'Fourth Option',
        'option5': 'Fifth Option',
        'option6': 'Sixth Option'
    }
    menu = Menu('Make your choice:', 'option1', choices)
    reply = menu.choose()"""
)
