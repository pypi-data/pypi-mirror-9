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
    name='reahl',
    version='3.1.0',
    description='The Reahl web framework.',
    long_description='Reahl is a web application framework for Python programmers.\n\nWith Reahl, programming is done purely in Python, using concepts familiar from GUI programming---like reusable Widgets and Events. There\'s no need for a programmer to know several different languages (HTML, JavaScript, template languages, etc) or to keep up with the tricks of these trades. The abstractions presented by Reahl relieve the programmer from the burden of dealing with the annoying problems of the web: security, accessibility, progressive enhancement (or graceful degradation) and browser quirks.\n\nReahl consists of many different eggs that are not all needed all of the time. This package does not contain much itself, but is an entry point for installing a set of Reahl eggs:\n\nInstall Reahl by installing with extras, eg: pip install "reahl[declarative,sqlite,dev,doc]" to install everything needed to run Reahl on sqlite, the dev tools and documentation. (On Windows platforms, use easy_install instead of pip.)\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for complete installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=[],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=[],
    install_requires=[],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=[],
    test_suite='tests',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={'sqlite': ['reahl-sqlitesupport>=3.1,<3.2'], 'doc': ['reahl-doc>=3.1,<3.2'], 'all': ['reahl-component>=3.1,<3.2', 'reahl-web>=3.1,<3.2', 'reahl-mailutil>=3.1,<3.2', 'reahl-sqlalchemysupport>=3.1,<3.2', 'reahl-web-declarative>=3.1,<3.2', 'reahl-domain>=3.1,<3.2', 'reahl-domainui>=3.1,<3.2', 'reahl-postgresqlsupport>=3.1,<3.2', 'reahl-sqlitesupport>=3.1,<3.2', 'reahl-dev>=3.1,<3.2', 'reahl-webdev>=3.1,<3.2', 'reahl-stubble>=3.1,<3.2', 'reahl-tofu>=3.1,<3.2', 'reahl-doc>=3.1,<3.2'], 'web': ['reahl-component>=3.1,<3.2', 'reahl-web>=3.1,<3.2', 'reahl-mailutil>=3.1,<3.2'], 'dev': ['reahl-dev>=3.1,<3.2', 'reahl-webdev>=3.1,<3.2', 'reahl-stubble>=3.1,<3.2', 'reahl-tofu>=3.1,<3.2'], 'declarative': ['reahl-sqlalchemysupport>=3.1,<3.2', 'reahl-web-declarative>=3.1,<3.2', 'reahl-domain>=3.1,<3.2', 'reahl-domainui>=3.1,<3.2'], 'elixir': ['reahl-sqlalchemysupport>=2.1,<2.2', 'reahl-domain>=2.1,<2.2', 'reahl-domainui>=2.1,<2.2', 'reahl-web-elixirimpl>=2.1,<2.2', 'reahl-web-elixirimpl'], 'postgresql': ['reahl-postgresqlsupport>=3.1,<3.2']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
