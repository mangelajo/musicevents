from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from .models import Artist, Venue, Event
from .utils.ticketmaster import sync_events_for_city


class MusicEventsAdminSite(admin.AdminSite):
    site_header = 'Music Events Admin'
    site_title = 'Music Events Admin Portal'
    index_title = 'Music Events Administration'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ticketmaster-sync/', self.admin_view(self.ticketmaster_sync_view), name='ticketmaster_sync'),
        ]
        return custom_urls + urls
    
    def ticketmaster_sync_view(self, request):
        # Redirect to the Ticketmaster sync page
        return redirect('events:ticketmaster_sync')


# Use the custom admin site
admin_site = MusicEventsAdminSite(name='music_events_admin')

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'capacity')
    list_filter = ('city', 'state')
    search_fields = ('name', 'address', 'city')

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'display_artists', 'ticket_price', 'external_id')
    list_filter = ('date', 'venue')
    search_fields = ('title', 'description', 'external_id')
    date_hierarchy = 'date'
    filter_horizontal = ('artists',)
    readonly_fields = ('external_id',)
    
    def display_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artists.all()[:3]])
    
    display_artists.short_description = 'Artists'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ticketmaster-sync/', self.admin_site.admin_view(lambda r: redirect('events:ticketmaster_sync')), 
                 name='ticketmaster_sync_redirect'),
        ]
        return custom_urls + urls


# Register with the default admin site
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Event, EventAdmin)

# Register with our custom admin site
admin_site.register(Artist, ArtistAdmin)
admin_site.register(Venue, VenueAdmin)
admin_site.register(Event, EventAdmin)
