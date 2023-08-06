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
    name='reahl-dev',
    version='3.1.0',
    description='The core Reahl development tools.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-dev is the component containing general Reahl development tools.\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.dev_dev', 'reahl.dev'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-component>=3.1,<3.2', 'reahl-tofu>=3.1,<3.2', 'Babel>=1.3,<1.3.9999', 'twine>=1.4.0,<1.4.9999', 'wheel>=0.24.0,<0.24.9999', 'reahl-bzrsupport>=3.1,<3.2'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=['nose', 'reahl-tofu>=3.1,<3.2', 'reahl-stubble>=3.1,<3.2'],
    test_suite='reahl.dev_dev',
    entry_points={
        'reahl.dev.commands': [
            'Refresh = reahl.dev.devshell:Refresh',
            'ExplainLegend = reahl.dev.devshell:ExplainLegend',
            'List = reahl.dev.devshell:List',
            'Select = reahl.dev.devshell:Select',
            'ClearSelection = reahl.dev.devshell:ClearSelection',
            'ListSelections = reahl.dev.devshell:ListSelections',
            'Save = reahl.dev.devshell:Save',
            'Read = reahl.dev.devshell:Read',
            'DeleteSelection = reahl.dev.devshell:DeleteSelection',
            'Shell = reahl.dev.devshell:Shell',
            'Setup = reahl.dev.devshell:Setup',
            'Build = reahl.dev.devshell:Build',
            'ListMissingDependencies = reahl.dev.devshell:ListMissingDependencies',
            'DebInstall = reahl.dev.devshell:DebInstall',
            'Upload = reahl.dev.devshell:Upload',
            'MarkReleased = reahl.dev.devshell:MarkReleased',
            'SubstVars = reahl.dev.devshell:SubstVars',
            'Debianise = reahl.dev.devshell:Debianise',
            'Info = reahl.dev.devshell:Info',
            'DevPiTest = reahl.dev.devshell:DevPiTest',
            'DevPiPush = reahl.dev.devshell:DevPiPush',
            'ExtractMessages = reahl.dev.devshell:ExtractMessages',
            'MergeTranslations = reahl.dev.devshell:MergeTranslations',
            'CompileTranslations = reahl.dev.devshell:CompileTranslations',
            'AddLocale = reahl.dev.devshell:AddLocale',
            'UpdateAptRepository = reahl.dev.devshell:UpdateAptRepository',
            'ServeSMTP = reahl.dev.mailtest:ServeSMTP'    ],
        'console_scripts': [
            'reahl = reahl.dev.devshell:WorkspaceCommandline.execute_one'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.dev.xmlclasses': [
            'MetaInfo = reahl.dev.devdomain:MetaInfo',
            'HardcodedMetadata = reahl.dev.devdomain:HardcodedMetadata',
            'DebianPackageMetadata = reahl.dev.devdomain:DebianPackageMetadata',
            'BzrSourceControl = reahl.dev.devdomain:BzrSourceControl',
            'Project = reahl.dev.devdomain:Project',
            'ChickenProject = reahl.dev.devdomain:ChickenProject',
            'EggProject = reahl.dev.devdomain:EggProject',
            'DebianPackage = reahl.dev.devdomain:DebianPackage',
            'DebianPackageSet = reahl.dev.devdomain:DebianPackageSet',
            'SshRepository = reahl.dev.devdomain:SshRepository',
            'PythonSourcePackage = reahl.dev.devdomain:PythonSourcePackage',
            'PythonWheelPackage = reahl.dev.devdomain:PythonWheelPackage',
            'PackageIndex = reahl.dev.devdomain:PackageIndex',
            'Dependency = reahl.dev.devdomain:Dependency',
            'ThirdpartyDependency = reahl.dev.devdomain:ThirdpartyDependency',
            'XMLDependencyList = reahl.dev.devdomain:XMLDependencyList',
            'ExtrasList = reahl.dev.devdomain:ExtrasList',
            'EntryPointExport = reahl.dev.devdomain:EntryPointExport',
            'ScriptExport = reahl.dev.devdomain:ScriptExport',
            'NamespaceList = reahl.dev.devdomain:NamespaceList',
            'NamespaceEntry = reahl.dev.devdomain:NamespaceEntry',
            'PersistedClassesList = reahl.dev.devdomain:PersistedClassesList',
            'OrderedPersistedClass = reahl.dev.devdomain:OrderedPersistedClass',
            'FileList = reahl.dev.devdomain:FileList',
            'AttachmentList = reahl.dev.devdomain:AttachmentList',
            'ShippedFile = reahl.dev.devdomain:ShippedFile',
            'MigrationList = reahl.dev.devdomain:MigrationList',
            'ConfigurationSpec = reahl.dev.devdomain:ConfigurationSpec',
            'ScheduledJobSpec = reahl.dev.devdomain:ScheduledJobSpec',
            'ExcludedPackage = reahl.dev.devdomain:ExcludedPackage',
            'TranslationPackage = reahl.dev.devdomain:TranslationPackage',
            'CommandAlias = reahl.dev.devdomain:CommandAlias',
            'ExtraPath = reahl.dev.devdomain:ExtraPath',
            'ProjectTag = reahl.dev.devdomain:ProjectTag'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
