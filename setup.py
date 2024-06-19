"""

"""

from pygitissue2todoist import __version__

from setuptools import setup

APP = ['pygitissue2todoist/PyGitIssue2Todoist.py']
DATA_FILES = [('pygitissue2todoist/resources', ['pygitissue2todoist/resources/loggingConfiguration.json']),
              ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/play.png']),
              ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/version.txt']),
              ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/packageversions.txt']),
              ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/SimpleHelp.html'])
              ]
OPTIONS = {}

setup(
    name='PyGitIssue2Todoist',
    version=__version__,
    app=APP,
    data_files=DATA_FILES,
    packages=['pygitissue2todoist',
              'pygitissue2todoist.adapters',
              'pygitissue2todoist.general',
              'pygitissue2todoist.general.exceptions',
              'pygitissue2todoist.resources',
              'pygitissue2todoist.ui',
              'pygitissue2todoist.ui.dialogs',
              'pygitissue2todoist.ui.dialogs.configuration',
              'pygitissue2todoist.ui.eventengine',
              ],
    include_package_data=True,
    zip_safe=False,

    url='https://github.com/hasii2011/PyGitIssue2Todoist',
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Convert Github issues to Todoist Tasks',
    options=dict(py2app=dict(
                    plist=dict(
                        CFBundleIdentifier='PyGitIssue2Todoist',
                        CFBundleShortVersionString=__version__,
                        LSEnvironment=dict(
                            APP_MODE='True',
                            PYTHONOPTIMIZE='1'
                        ),
                        LSMultipleInstancesProhibited='True',
                    ),
            ),
    ),
    setup_requires=['py2app'],
    install_requires=['codeallybasic==1.3.2', 'wxPython==4.2.1', 'PyGithub==2.3.0', 'todoist_api_python==2.1.5']
)
