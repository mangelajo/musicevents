from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from events.models import Event, Artist, Venue
import datetime

class EventListViewPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a venue for our events
        venue = Venue.objects.create(
            name='Test Venue',
            address='123 Test St',
            city='Test City',
            state='Test State',
            zip_code='12345'
        )
        
        # Create an artist for our events
        artist = Artist.objects.create(
            name='Test Artist',
            bio='Test Bio'
        )
        
        # Create 15 future events (for pagination testing)
        now = timezone.now()
        for i in range(15):
            event = Event.objects.create(
                title=f'Future Event {i+1}',
                description=f'Description for future event {i+1}',
                date=now + datetime.timedelta(days=i+1),
                venue=venue,
                slug=f'future-event-{i+1}'
            )
            event.artists.add(artist)
        
        # Create 5 past events
        for i in range(5):
            event = Event.objects.create(
                title=f'Past Event {i+1}',
                description=f'Description for past event {i+1}',
                date=now - datetime.timedelta(days=i+1),
                venue=venue,
                slug=f'past-event-{i+1}'
            )
            event.artists.add(artist)

    def setUp(self):
        self.client = Client()
    
    def test_event_list_pagination(self):
        """Test that the event list view paginates correctly"""
        # Get the first page
        response = self.client.get(reverse('events:event_list'))
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        self.assertTemplateUsed(response, 'events/event_list.html')
        
        # Check that pagination is working
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        
        # Check that we have the correct number of events on the first page (9 per page)
        self.assertEqual(len(response.context['events']), 9)
        
        # Check that we have the correct page object
        self.assertEqual(response.context['page_obj'].number, 1)
        
        # Check that we have the correct paginator object
        self.assertEqual(response.context['paginator'].num_pages, 2)
        self.assertEqual(response.context['paginator'].count, 15)
    
    def test_event_list_second_page(self):
        """Test that the second page of the event list works correctly"""
        # Get the second page
        response = self.client.get(reverse('events:event_list') + '?page=2')
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that we have the correct number of events on the second page (6 remaining events)
        self.assertEqual(len(response.context['events']), 6)
        
        # Check that we have the correct page object
        self.assertEqual(response.context['page_obj'].number, 2)
    
    def test_event_list_invalid_page(self):
        """Test that an invalid page number returns a 404 error"""
        # Get an invalid page
        response = self.client.get(reverse('events:event_list') + '?page=999')
        
        # Check that the response is 404 Not Found (Django's default behavior for invalid pages)
        self.assertEqual(response.status_code, 404)
    
    def test_past_events_not_paginated(self):
        """Test that past events are not paginated and limited to 5"""
        # Get the first page
        response = self.client.get(reverse('events:event_list'))
        
        # Check that past_events is in the context
        self.assertTrue('past_events' in response.context)
        
        # Check that we have exactly 5 past events
        self.assertEqual(len(response.context['past_events']), 5)
        
        # Check that the past events are ordered by date in descending order
        dates = [event.date for event in response.context['past_events']]
        self.assertEqual(dates, sorted(dates, reverse=True))


class ArtistListViewPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 15 artists for pagination testing
        for i in range(15):
            Artist.objects.create(
                name=f'Test Artist {i+1}',
                bio=f'Bio for test artist {i+1}'
            )
    
    def setUp(self):
        self.client = Client()
    
    def test_artist_list_pagination(self):
        """Test that the artist list view paginates correctly"""
        # Get the first page
        response = self.client.get(reverse('events:artist_list'))
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that pagination is working
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        
        # Check that we have the correct number of artists on the first page (12 per page)
        self.assertEqual(len(response.context['artists']), 12)
        
        # Check that we have the correct page object
        self.assertEqual(response.context['page_obj'].number, 1)
        
        # Check that we have the correct paginator object
        self.assertEqual(response.context['paginator'].num_pages, 2)
        self.assertEqual(response.context['paginator'].count, 15)
    
    def test_artist_list_second_page(self):
        """Test that the second page of the artist list works correctly"""
        # Get the second page
        response = self.client.get(reverse('events:artist_list') + '?page=2')
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that we have the correct number of artists on the second page (3 remaining artists)
        self.assertEqual(len(response.context['artists']), 3)
        
        # Check that we have the correct page object
        self.assertEqual(response.context['page_obj'].number, 2)


class VenueListViewPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 15 venues for pagination testing
        for i in range(15):
            Venue.objects.create(
                name=f'Test Venue {i+1}',
                address=f'123 Test St {i+1}',
                city='Test City',
                state='Test State',
                zip_code='12345'
            )
    
    def setUp(self):
        self.client = Client()
    
    def test_venue_list_pagination(self):
        """Test that the venue list view paginates correctly"""
        # Get the first page
        response = self.client.get(reverse('events:venue_list'))
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that pagination is working
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        
        # Check that we have the correct number of venues on the first page (12 per page)
        self.assertEqual(len(response.context['venues']), 12)
        
        # Check that we have the correct page object
        self.assertEqual(response.context['page_obj'].number, 1)
        
        # Check that we have the correct paginator object
        self.assertEqual(response.context['paginator'].num_pages, 2)
        self.assertEqual(response.context['paginator'].count, 15)
    
    def test_venue_list_second_page(self):
        """Test that the second page of the venue list works correctly"""
        # Get the second page
        response = self.client.get(reverse('events:venue_list') + '?page=2')
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that we have the correct number of venues on the second page (3 remaining venues)
        self.assertEqual(len(response.context['venues']), 3)
        
        # Check that we have the correct page object
        self.assertEqual(response.context['page_obj'].number, 2)