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
    name='reahl-web',
    version='3.1.0',
    description='The core Reahl web framework',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis package contains the core of the Reahl framework.\n\nSee http://www.reahl.org/docs/3.1/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.web', 'reahl.messages', 'reahl.web_dev', 'reahl.web.static', 'reahl.web_dev.appstructure', 'reahl.web_dev.advanced', 'reahl.web_dev.widgets', 'reahl.web_dev.inputandvalidation', 'reahl.web.static.jquery', 'reahl.web_dev.advanced.subresources'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['reahl-component>=3.1,<3.2', 'slimit>=0.8,<0.8.999', 'cssmin>=0.2,<0.2.999', 'BeautifulSoup4>=4.3,<4.3.999', 'webob>=1.4,<1.4.999', 'Babel>=1.3,<1.3.999'],
    setup_requires=['reahl-bzrsupport>=3.1,<3.2'],
    tests_require=['nose', 'reahl-tofu>=3.1,<3.2', 'reahl-stubble>=3.1,<3.2', 'reahl-sqlalchemysupport>=3.1,<3.2', 'reahl-postgresqlsupport>=3.1,<3.2', 'reahl-web-declarative>=3.1,<3.2', 'reahl-domain>=3.1,<3.2', 'reahl-webdev>=3.1,<3.2', 'reahl-dev>=3.1,<3.2'],
    test_suite='reahl.web_dev',
    entry_points={
        'reahl.persistlist': [
            '0 = reahl.web.pager:SequentialPageIndex'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.attachments.js': [
            '0:reahl/web/reahl.hashchange.js = reahl',
            '1:reahl/web/reahl.ajaxlink.js = reahl',
            '2:reahl/web/reahl.form.js = reahl',
            '3:reahl/web/reahl.textinput.js = reahl',
            '4:reahl/web/reahl.cueinput.js = reahl',
            '5:reahl/web/reahl.labeloverinput.js = reahl',
            '6:reahl/web/reahl.fileuploadli.js = reahl',
            '7:reahl/web/reahl.fileuploadpanel.js = reahl',
            '8:reahl/web/reahl.popupa.js = reahl',
            '9:reahl/web/reahl.slidingpanel.js = reahl'    ],
        'reahl.translations': [
            'reahl-web = reahl.messages'    ],
        'reahl.configspec': [
            'config = reahl.web.egg:WebConfig'    ],
        'reahl.attachments.any': [
            '0:reahl/web/static/runningon.png = reahl'    ],
        'reahl.attachments.css': [
            '0:reahl/web/reahl.labelledinput.css = reahl',
            '1:reahl/web/reahl.labeloverinput.css = reahl',
            '2:reahl/web/reahl.menu.css = reahl',
            '3:reahl/web/reahl.hmenu.css = reahl',
            '4:reahl/web/reahl.slidingpanel.css = reahl',
            '5:reahl/web/reahl.runningonbadge.css = reahl'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
