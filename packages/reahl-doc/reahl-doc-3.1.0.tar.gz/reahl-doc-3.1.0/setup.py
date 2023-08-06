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
    name='reahl-doc',
    version='3.1.0',
    description='Documentation and examples for Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-doc contains documentation and examples of Reahl.\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.doc_dev', 'reahl.doc', 'reahl.doc.examples', 'reahl.doc.examples.tutorial', 'reahl.doc.examples.features', 'reahl.doc.examples.tutorial.login2', 'reahl.doc.examples.tutorial.datatable', 'reahl.doc.examples.tutorial.parameterised2', 'reahl.doc.examples.tutorial.ajax', 'reahl.doc.examples.tutorial.hello', 'reahl.doc.examples.tutorial.migrationexample', 'reahl.doc.examples.tutorial.access1', 'reahl.doc.examples.tutorial.sessionscope', 'reahl.doc.examples.tutorial.login1', 'reahl.doc.examples.tutorial.addressbook2', 'reahl.doc.examples.tutorial.pager', 'reahl.doc.examples.tutorial.hellonginx', 'reahl.doc.examples.tutorial.componentconfig', 'reahl.doc.examples.tutorial.table', 'reahl.doc.examples.tutorial.slots', 'reahl.doc.examples.tutorial.helloapache', 'reahl.doc.examples.tutorial.addressbook1', 'reahl.doc.examples.tutorial.pageflow1', 'reahl.doc.examples.tutorial.access2', 'reahl.doc.examples.tutorial.jobs', 'reahl.doc.examples.tutorial.parameterised1', 'reahl.doc.examples.tutorial.access', 'reahl.doc.examples.tutorial.pageflow2', 'reahl.doc.examples.tutorial.i18nexample', 'reahl.doc.examples.features.pageflow', 'reahl.doc.examples.features.persistence', 'reahl.doc.examples.features.validation', 'reahl.doc.examples.features.layout', 'reahl.doc.examples.features.slidingpanel', 'reahl.doc.examples.features.tabbedpanel', 'reahl.doc.examples.features.access', 'reahl.doc.examples.features.i18nexample', 'reahl.doc.examples.tutorial.login2.login2_dev', 'reahl.doc.examples.tutorial.datatable.datatable_dev', 'reahl.doc.examples.tutorial.parameterised2.parameterised2_dev', 'reahl.doc.examples.tutorial.ajax.ajax_dev', 'reahl.doc.examples.tutorial.migrationexample.migrationexample_dev', 'reahl.doc.examples.tutorial.access1.access1_dev', 'reahl.doc.examples.tutorial.sessionscope.sessionscope_dev', 'reahl.doc.examples.tutorial.login1.login1_dev', 'reahl.doc.examples.tutorial.addressbook2.addressbook2_dev', 'reahl.doc.examples.tutorial.pager.pager_dev', 'reahl.doc.examples.tutorial.componentconfig.componentconfig_dev', 'reahl.doc.examples.tutorial.table.table_dev', 'reahl.doc.examples.tutorial.addressbook1.addressbook1_dev', 'reahl.doc.examples.tutorial.access2.access2_dev', 'reahl.doc.examples.tutorial.jobs.jobs_dev', 'reahl.doc.examples.tutorial.access.access_dev', 'reahl.doc.examples.tutorial.i18nexample.i18nexample_dev', 'reahl.doc.examples.tutorial.i18nexample.i18nexamplemessages'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-web>=3.1,<3.2', 'reahl-component>=3.1,<3.2', 'reahl-sqlalchemysupport>=3.1,<3.2', 'reahl-web-declarative>=3.1,<3.2', 'reahl-domain>=3.1,<3.2', 'reahl-domainui>=3.1,<3.2'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=['nose', 'reahl-tofu>=3.1,<3.2', 'Sphinx', 'reahl-stubble>=3.1,<3.2', 'reahl-dev>=3.1,<3.2', 'reahl-webdev>=3.1,<3.2', 'reahl-postgresqlsupport>=3.1,<3.2', 'reahl-sqlitesupport>=3.1,<3.2'],
    test_suite='reahl.doc_dev',
    entry_points={
        'reahl.persistlist': [
            '0 = reahl.doc.examples.features.persistence.persistence:Comment',
            '1 = reahl.doc.fileupload:Comment',
            '2 = reahl.doc.fileupload:AttachedFile',
            '3 = reahl.doc.examples.tutorial.addressbook2.addressbook2:Address',
            '4 = reahl.doc.examples.tutorial.addressbook1.addressbook1:Address',
            '5 = reahl.doc.examples.tutorial.pageflow2.pageflow2:Address',
            '6 = reahl.doc.examples.tutorial.pageflow1.pageflow1:Address',
            '7 = reahl.doc.examples.tutorial.parameterised1.parameterised1:Address',
            '8 = reahl.doc.examples.tutorial.parameterised2.parameterised2:Address',
            '9 = reahl.doc.examples.tutorial.sessionscope.sessionscope:User',
            '10 = reahl.doc.examples.tutorial.sessionscope.sessionscope:LoginSession',
            '11 = reahl.doc.examples.tutorial.access1.access1:AddressBook',
            '12 = reahl.doc.examples.tutorial.access1.access1:Collaborator',
            '13 = reahl.doc.examples.tutorial.access1.access1:Address',
            '14 = reahl.doc.examples.tutorial.access2.access2:AddressBook',
            '15 = reahl.doc.examples.tutorial.access2.access2:Collaborator',
            '16 = reahl.doc.examples.tutorial.access2.access2:Address',
            '17 = reahl.doc.examples.tutorial.access.access:AddressBook',
            '18 = reahl.doc.examples.tutorial.access.access:Collaborator',
            '19 = reahl.doc.examples.tutorial.access.access:Address',
            '20 = reahl.doc.examples.tutorial.i18nexample.i18nexample:Address',
            '21 = reahl.doc.examples.tutorial.componentconfig.componentconfig:Address',
            '22 = reahl.doc.examples.tutorial.migrationexample.migrationexample:Address',
            '23 = reahl.doc.examples.tutorial.jobs.jobs:Address',
            '24 = reahl.doc.examples.tutorial.table.table:Address',
            '25 = reahl.doc.examples.tutorial.datatable.datatable:Address'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.dev.commands': [
            'GetExample = reahl.doc.commands:GetExample',
            'ListExamples = reahl.doc.commands:ListExamples'    ],
        'reahl.translations': [
            'reahl-doc = reahl.doc.examples.tutorial.i18nexample.i18nexamplemessages'    ],
        'reahl.configspec': [
            'config = reahl.doc.examples.tutorial.componentconfig.componentconfig:AddressConfig'    ],
        'reahl.scheduled_jobs': [
            'Address.clear_added_flags = reahl.doc.examples.tutorial.jobs.jobs:Address.clear_added_flags'    ],
                 },
    extras_require={'pillow': ['pillow']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
