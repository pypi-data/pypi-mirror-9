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
    name='reahl-sqlalchemysupport',
    version='3.1.0',
    description='Support for using SqlAlchemy with Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis package contains infrastructure necessary to use Reahl with SqlAlchemy or Elixir.\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.sqlalchemysupport_dev', 'reahl.sqlalchemysupport'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-component>=3.1,<3.2', 'sqlalchemy>=0.9.2,<0.9.999', 'alembic>=0.6,<0.6.999'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=['nose', 'reahl-sqlitesupport>=3.1,<3.2', 'reahl-domain>=3.1,<3.2', 'reahl-dev>=3.1,<3.2', 'reahl-tofu>=3.1,<3.2', 'reahl-stubble>=3.1,<3.2'],
    test_suite='reahl.sqlalchemysupport_dev',
    entry_points={
        'reahl.configspec': [
            'config = reahl.sqlalchemysupport:SqlAlchemyConfig'    ],
        'reahl.persistlist': [
            '0 = reahl.sqlalchemysupport:SchemaVersion'    ],
        'reahl.migratelist': [
            '0 = reahl.sqlalchemysupport.elixirmigration:ElixirToDeclarativeSqlAlchemySupportChanges'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
