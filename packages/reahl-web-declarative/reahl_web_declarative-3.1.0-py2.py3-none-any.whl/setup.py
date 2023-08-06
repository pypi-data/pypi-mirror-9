from setuptools import setup, Command
class InstallTestDependencies(Command):
    user_options = []
    def run(self):
        from setuptools.command import easy_install
        easy_install.main(self.distribution.tests_require)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

setup(
    name='reahl-web-declarative',
    version='3.1.0',
    description='An implementation of Reahl persisted classes using Elixir.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nSome core elements of Reahl can be implemented for use with different persistence technologies. This is such an implementation based on SqlAlchemy/Elixir.\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.webdeclarative', 'reahl.webdeclarative_dev'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-sqlalchemysupport>=3.1,<3.2', 'reahl-web>=3.1,<3.2', 'reahl-component>=3.1,<3.2'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=['nose', 'reahl-tofu>=3.1,<3.2', 'reahl-stubble>=3.1,<3.2', 'reahl-dev>=3.1,<3.2', 'reahl-webdev>=3.1,<3.2', 'reahl-postgresqlsupport>=3.1,<3.2'],
    test_suite='reahl.webdeclarative_dev',
    entry_points={
        'reahl.scheduled_jobs': [
            'UserSession.remove_dead_sessions = reahl.webdeclarative.webdeclarative:UserSession.remove_dead_sessions'    ],
        'reahl.configspec': [
            'config = reahl.webdeclarative.webdeclarative:WebDeclarativeConfig'    ],
        'reahl.persistlist': [
            '0 = reahl.webdeclarative.webdeclarative:UserSession',
            '1 = reahl.webdeclarative.webdeclarative:SessionData',
            '2 = reahl.webdeclarative.webdeclarative:UserInput',
            '3 = reahl.webdeclarative.webdeclarative:PersistedException',
            '4 = reahl.webdeclarative.webdeclarative:PersistedFile'    ],
        'reahl.migratelist': [
            '0 = reahl.webdeclarative.migrations:RenameRegionToUi',
            '1 = reahl.webdeclarative.migrations:ElixirToDeclarativeWebDeclarativeChanges',
            '2 = reahl.webdeclarative.migrations:MergeWebUserSessionToUserSession',
            '3 = reahl.webdeclarative.migrations:RenameContentType'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
