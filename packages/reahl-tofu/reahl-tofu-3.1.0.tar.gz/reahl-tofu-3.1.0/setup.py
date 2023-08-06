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
    name='reahl-tofu',
    version='3.1.0',
    description='A testing framework that couples fixtures and tests loosely.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nTofu is part of the Reahl development tools. Tofu can be used independently of the Reahl web framework.\n\nTofu allows you to have a hierarchy of test fixtures that is *completely* decoupled from your hierarchy of tests or test suites. Tofu includes a number of other related test utilities. It also includes a plugin for nosetests that makes using it with nose seamless.\n\nTofu can also be used to run the set_ups of fixtures from the command line.  This is useful for acceptance tests whose fixtures create data in databases that can be used for demonstration and user testing. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['tofu_test', 'reahl', 'devenv', 'examples', 'reahl.tofu', 'reahl.tofu_dev'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['six'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=['nose', 'reahl-stubble>=3.1,<3.2', 'reahl-tofu>=3.1,<3.2'],
    test_suite='reahl.tofu_dev',
    entry_points={
        'nose.plugins.0.10': [
            'run-fixture = reahl.tofu.nosesupport:RunFixturePlugin',
            'long-output = reahl.tofu.nosesupport:LongOutputPlugin',
            'test-directory = reahl.tofu.nosesupport:TestDirectoryPlugin',
            'log-level = reahl.tofu.nosesupport:LogLevelPlugin',
            'setup-fixture = reahl.tofu.nosesupport:SetUpFixturePlugin',
            'all-tests = reahl.tofu.nosesupport:MarkedTestsPlugin'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
