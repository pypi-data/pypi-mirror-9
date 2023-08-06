import os
import contextlib

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.contrib.admin.tests import AdminSeleniumWebDriverTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    visibility_of_element_located, element_to_be_clickable)

from .helpers import CropdusterTestCaseMediaMixin
from .models import Article, Author
from ..models import Size


class TestAdmin(CropdusterTestCaseMediaMixin, AdminSeleniumWebDriverTestCase):

    urls = 'cropduster.tests.urls'

    available_apps = [
        'grappelli',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.messages',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'generic_plus',
        'cropduster',
    ]

    webdriver_class = 'selenium.webdriver.phantomjs.webdriver.WebDriver'

    def setUp(self):
        super(TestAdmin, self).setUp()
        self.selenium.set_window_size(1120, 550)
        User.objects.create_superuser('mtwain', 'me@example.com', 'p@ssw0rd')
        self.admin_login("mtwain", "p@ssw0rd", login_url=reverse('admin:index'))

    def wait_until_visible_selector(self, selector, timeout=10):
        self.wait_until(
            visibility_of_element_located((By.CSS_SELECTOR, selector)),
            timeout=timeout)

    def wait_until_clickable_xpath(self, xpath, timeout=10):
        self.wait_until(
            element_to_be_clickable((By.XPATH, xpath)), timeout=timeout)

    def wait_until_clickable_selector(self, selector, timeout=10):
        self.wait_until(
            element_to_be_clickable((By.CSS_SELECTOR, selector)),
            timeout=timeout)

    @contextlib.contextmanager
    def visible_selector(self, selector, timeout=10):
        self.wait_until_visible_selector(selector, timeout)
        yield self.selenium.find_element_by_css_selector(selector)

    @contextlib.contextmanager
    def clickable_selector(self, selector, timeout=10):
        self.wait_until_clickable_selector(selector, timeout)
        yield self.selenium.find_element_by_css_selector(selector)

    @contextlib.contextmanager
    def clickable_xpath(self, xpath, timeout=10):
        self.wait_until_clickable_xpath(xpath, timeout)
        yield self.selenium.find_element_by_xpath(xpath)

    @contextlib.contextmanager
    def switch_to_popup_window(self):
        self.wait_until(lambda d: len(d.window_handles) == 2)
        self.selenium.switch_to.window(self.selenium.window_handles[1])
        yield
        self.wait_until(lambda d: len(d.window_handles) == 1)
        self.selenium.switch_to.window(self.selenium.window_handles[0])

    def test_addform_single_image(self):
        browser = self.selenium
        browser.get(self.live_server_url + reverse('admin:cropduster_author_add'))
        browser.find_element_by_id('id_name').send_keys('Mark Twain')
        browser.find_element_by_css_selector('#headshot-group .rounded-button').click()

        with self.switch_to_popup_window():
            with self.visible_selector('#id_image') as el:
                el.send_keys(os.path.join(self.TEST_IMG_DIR, 'img.jpg'))
            with self.clickable_selector('#upload-button') as el:
                el.click()
            with self.clickable_selector('#crop-button') as el:
                el.click()

        with self.clickable_xpath('//input[@value="Save and continue editing"]') as el:
            el.click()

        author = Author.objects.all()[0]
        sizes = list(Size.flatten(Author.HEADSHOT_SIZES))
        self.assertTrue(bool(author.headshot.path))
        self.assertEqual(len(author.headshot.related_object.thumbs.all()), len(sizes))

    def test_addform_multiple_image(self):
        author = Author.objects.create(name="Mark Twain")

        browser = self.selenium
        browser.get(self.live_server_url + reverse('admin:cropduster_article_add'))

        browser.find_element_by_id('id_title').send_keys("A Connecticut Yankee in King Arthur's Court")

        # Upload and crop first Image
        browser.find_element_by_css_selector('#lead_image-group .rounded-button').click()

        with self.switch_to_popup_window():
            with self.visible_selector('#id_image') as el:
                el.send_keys(os.path.join(self.TEST_IMG_DIR, 'img.jpg'))
            with self.clickable_selector('#upload-button') as el:
                el.click()
            with self.clickable_selector('#crop-button') as el:
                el.click()
            with self.clickable_selector('#crop-button') as el:
                el.click()
            with self.clickable_selector('#crop-button') as el:
                el.click()

        # Upload and crop second Image
        with self.clickable_selector('#alt_image-group .rounded-button') as el:
            # With the Chrome driver, using Grappelli, this button can be covered
            # by the fixed footer. So we scroll the button into view.
            browser.execute_script('window.scrollTo(0, %d)' % el.location['y'])
            el.click()

        with self.switch_to_popup_window():
            with self.visible_selector('#id_image') as el:
                el.send_keys(os.path.join(self.TEST_IMG_DIR, 'img.png'))
            with self.clickable_selector('#upload-button') as el:
                el.click()
            with self.clickable_selector('#crop-button') as el:
                el.click()
            with self.clickable_selector('#crop-button') as el:
                el.click()

        # Add required FK
        browser.find_element_by_xpath('//select[@id="id_author"]/option[@value=%d]' % author.pk).click()
        browser.find_element_by_xpath('//input[@value="Save and continue editing"]').click()

        # Test that crops saved correctly
        article = Article.objects.all()[0]
        lead_sizes = list(Size.flatten(Article.LEAD_IMAGE_SIZES))
        alt_sizes = list(Size.flatten(Article.ALT_IMAGE_SIZES))

        self.assertTrue(article.lead_image.path.endswith('.jpg'))
        self.assertEqual(len(article.lead_image.related_object.thumbs.all()), len(lead_sizes))
        self.assertTrue(article.alt_image.path.endswith('.png'))
        self.assertEqual(len(article.alt_image.related_object.thumbs.all()), len(alt_sizes))

    def test_changeform_single_image(self):
        author = Author.objects.create(name="Samuel Langhorne Clemens",
            headshot=os.path.join(self.TEST_IMG_DIR_RELATIVE, 'img.jpg'))
        author.headshot.generate_thumbs()

        url = reverse('admin:cropduster_author_change', args=(author.pk, ))
        browser = self.selenium
        browser.get(self.live_server_url + url)
        elem = browser.find_element_by_id('id_name')
        elem.clear()
        elem.send_keys("Mark Twain")
        old_page_id = browser.find_element_by_tag_name('html').id
        browser.find_element_by_xpath('//input[@value="Save and continue editing"]').click()
        self.wait_until(lambda b: b.find_element_by_tag_name('html').id != old_page_id)
        self.assertEqual(Author.objects.get(pk=author.pk).name, 'Mark Twain')

    def test_changeform_multiple_images(self):
        author = Author.objects.create(name="Samuel Langhorne Clemens")
        article = Article.objects.create(title="title", author=author,
            lead_image=os.path.join(self.TEST_IMG_DIR_RELATIVE, 'img.jpg'),
            alt_image=os.path.join(self.TEST_IMG_DIR_RELATIVE, 'img.png'))
        article.lead_image.generate_thumbs()
        article.alt_image.generate_thumbs()

        url = reverse('admin:cropduster_article_change', args=(article.pk, ))
        browser = self.selenium
        browser.get(self.live_server_url + url)
        elem = browser.find_element_by_id('id_title')
        elem.clear()
        elem.send_keys("Updated Title")
        old_page_id = browser.find_element_by_tag_name('html').id
        browser.find_element_by_xpath('//input[@value="Save and continue editing"]').click()
        self.wait_until(lambda b: b.find_element_by_tag_name('html').id != old_page_id)
        self.assertEqual(Article.objects.get(pk=article.pk).title, 'Updated Title')
