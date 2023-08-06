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
    name='reahl-webdev',
    version='3.1.0',
    description='Web-specific development tools for Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl development tools for testing and working with web based programs.\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.webdev'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-web>=3.1,<3.2', 'reahl-dev>=3.1,<3.2', 'reahl-component>=3.1,<3.2', 'reahl-tofu>=3.1,<3.2', 'reahl-domain>=3.1,<3.2', 'lxml>=3.3,<3.3.999', 'WebTest>=2.0,<2.0.999', 'selenium>=2.42,<2.42.999'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=[],
    test_suite='tests',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.dev.commands': [
            'ServeCurrentProject = reahl.webdev.commands:ServeCurrentProject'    ],
                 },
    extras_require={'pillow': ['pillow>=2.5,<2.5.999']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
