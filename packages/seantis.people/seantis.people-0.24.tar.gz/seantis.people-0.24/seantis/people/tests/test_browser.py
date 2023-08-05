from seantis.people import tests


class TestBrowser(tests.FunctionalTestCase):

    def setUp(self):
        super(TestBrowser, self).setUp()
        self.baseurl = self.portal.absolute_url()
        self.admin_browser = browser = self.new_admin_browser()

        browser.open(self.baseurl + '/createObject?type_name=Folder')
        browser.getControl('Title').value = 'testfolder'
        browser.getControl('Save').click()

        self.folder_url = self.baseurl + '/testfolder'
        self.infolder = lambda url: self.folder_url + url

    def tearDown(self):
        self.admin_browser.open(self.infolder('/delete_confirmation'))
        self.admin_browser.getControl('Delete').click()

        super(TestBrowser, self).tearDown()

    def new_admin_browser(self):
        browser = self.new_browser()
        browser.login_admin()

        return browser

    def new_people_list(self, title='testlist'):
        browser = self.new_admin_browser()

        browser.open(self.infolder('/++add++seantis.people.list'))
        browser.getControl(name='form.widgets.title').value = title
        browser.getControl('Save').click()

        return self.infolder('/{}'.format(title.lower()))

    def new_person(self, first_name, last_name, list_id='testlist'):
        browser = self.new_admin_browser()

        browser.open(
            self.infolder('/{}/++add++seantis.people.standard'.format(list_id))
        )

        browser.getControl('First Name').value = first_name
        browser.getControl('Last Name').value = last_name

        browser.getControl('Save').click()

    def test_empty_list(self):
        list_url = self.new_people_list()

        browser = self.new_admin_browser()
        browser.open(list_url)
        self.assertIn('No people in the list.', browser.contents)

        # layout policy
        self.assertNotIn('seantis-people-standard-list', browser.contents)

    def test_simple_list(self):
        list_url = self.new_people_list()
        self.new_person('Phil', 'Dunphy')

        browser = self.new_admin_browser()
        browser.open(list_url)
        self.assertIn('Phil', browser.contents)
        self.assertIn('Dunphy', browser.contents)

        # layout policy
        self.assertIn('seantis-people-standard-list', browser.contents)

    def test_remove_from_list(self):
        list_url = self.new_people_list()
        self.new_person('Claire', 'Dunphy')

        browser = self.new_admin_browser()
        browser.open(list_url)
        self.assertIn('Claire', browser.contents)
        self.assertIn('Dunphy', browser.contents)

        browser.open(list_url + '/dunphy-claire/delete_confirmation')
        browser.getControl('Delete').click()

        browser.open(list_url)
        self.assertNotIn('Claire', browser.contents)
        self.assertNotIn('Dunphy', browser.contents)
