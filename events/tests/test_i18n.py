from django.test import TestCase
from django.urls import reverse


class I18nTests(TestCase):
    def test_language_selector_present(self):
        """Test that the language selector is present on the home page"""
        response = self.client.get(reverse('events:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="language"')  # Check form field exists
        self.assertContains(response, '<select')  # Check select element exists
        self.assertContains(response, 'form action="/i18n/setlang/"')  # Check form action

    def test_language_switch(self):
        """Test switching between languages"""
        # Start with English by setting the cookie
        self.client.cookies['django_language'] = 'en'
        response = self.client.get(reverse('events:home'))
        self.assertEqual(response.status_code, 200)
        try:
            self.assertContains(response, 'Events')  # English menu item
        except AssertionError:
            print("\nResponse content (English):")
            print(response.content.decode())
            raise

        # Switch to Spanish
        response = self.client.post(reverse('set_language'), {
            'language': 'es',
            'next': '/'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        try:
            self.assertContains(response, 'Eventos')  # Spanish menu item
        except AssertionError:
            print("\nResponse content (Spanish):")
            print(response.content.decode())
            raise

        # Switch back to English
        response = self.client.post(reverse('set_language'), {
            'language': 'en',
            'next': '/'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        try:
            self.assertContains(response, 'Events')  # Back to English
        except AssertionError:
            print("\nResponse content (Back to English):")
            print(response.content.decode())
            raise