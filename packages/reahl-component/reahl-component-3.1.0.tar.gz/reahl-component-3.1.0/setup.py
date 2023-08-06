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
    name='reahl-component',
    version='3.1.0',
    description='The component framework of Reahl.',
    long_description="Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-component is the component that contains Reahl's component framework.\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for installation instructions. ",
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.component', 'reahl.messages', 'reahl.component_dev'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['six', 'Babel>=1.3,<1.3.9999', 'python-dateutil>=2.2,<2.2.999', 'wrapt>=1.10.2,<1.10.999'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=['nose', 'reahl-tofu>=3.1,<3.2', 'reahl-stubble>=3.1,<3.2'],
    test_suite='reahl.component_dev',
    entry_points={
        'reahl.component.databasecontrols': [
            'NullDatabaseControl = reahl.component.dbutils:NullDatabaseControl'    ],
        'reahl.translations': [
            'reahl-component = reahl.messages'    ],
        'reahl.component.prodcommands': [
            'CreateDBUser = reahl.component.prodshell:CreateDBUser',
            'DropDBUser = reahl.component.prodshell:DropDBUser',
            'CreateDB = reahl.component.prodshell:CreateDB',
            'DropDB = reahl.component.prodshell:DropDB',
            'BackupDB = reahl.component.prodshell:BackupDB',
            'RestoreDB = reahl.component.prodshell:RestoreDB',
            'BackupAllDB = reahl.component.prodshell:BackupAllDB',
            'RestoreAllDB = reahl.component.prodshell:RestoreAllDB',
            'SizeDB = reahl.component.prodshell:SizeDB',
            'RunJobs = reahl.component.prodshell:RunJobs',
            'CreateDBTables = reahl.component.prodshell:CreateDBTables',
            'DropDBTables = reahl.component.prodshell:DropDBTables',
            'MigrateDB = reahl.component.prodshell:MigrateDB',
            'DiffDB = reahl.component.prodshell:DiffDB',
            'ListConfig = reahl.component.prodshell:ListConfig',
            'CheckConfig = reahl.component.prodshell:CheckConfig',
            'ListDependencies = reahl.component.prodshell:ListDependencies'    ],
        'console_scripts': [
            'reahl-control = reahl.component.prodshell:ProductionCommandline.execute_one'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
