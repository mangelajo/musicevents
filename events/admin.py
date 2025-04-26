from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Artist, Venue, Event
from .utils.ticketmaster import sync_events_for_city
from .utils.riviera_sync import sync_riviera_events
from .utils.cafeberlin_sync import sync_cafeberlin_events
from django import forms


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
    list_display = ('name', 'website', 'has_spotify_data', 'spotify_followers', 'spotify_popularity')
    search_fields = ('name', 'spotify_id')
    list_filter = ('spotify_last_updated',)
    readonly_fields = ('spotify_id', 'spotify_uri', 'spotify_url', 'spotify_popularity', 
                      'spotify_followers', 'spotify_image_url', 'spotify_last_updated')
    fieldsets = (
        (None, {
            'fields': ('name', 'bio', 'website', 'image')
        }),
        ('Spotify Information', {
            'fields': ('spotify_id', 'spotify_uri', 'spotify_url', 'spotify_popularity', 
                      'spotify_followers', 'spotify_image_url', 'spotify_last_updated'),
            'classes': ('collapse',),
        }),
    )
    
    def has_spotify_data(self, obj):
        return bool(obj.spotify_id)
    has_spotify_data.boolean = True
    has_spotify_data.short_description = 'Spotify'
    
    actions = ['fetch_spotify_data']
    
    def fetch_spotify_data(self, request, queryset):
        updated = 0
        for artist in queryset:
            if artist.fetch_spotify_data(force_update=True):
                updated += 1
        
        if updated:
            self.message_user(request, f"Successfully updated Spotify data for {updated} artists.")
        else:
            self.message_user(request, "Could not find Spotify data for any of the selected artists.", level=messages.WARNING)
    
    fetch_spotify_data.short_description = "Fetch Spotify data for selected artists"

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'capacity')
    list_filter = ('city', 'state')
    search_fields = ('name', 'address', 'city')

class TicketmasterSyncForm(forms.Form):
    city = forms.CharField(max_length=100, required=True, help_text="Enter city name (e.g., 'New York')")
    state = forms.CharField(max_length=2, required=False, help_text="Enter state code (e.g., 'NY')")

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'display_artists', 'ticket_price', 'external_id')
    list_filter = ('date', 'venue')
    search_fields = ('title', 'description', 'external_id')
    date_hierarchy = 'date'
    filter_horizontal = ('artists',)
    readonly_fields = ('external_id',)
    change_list_template = 'admin/events/event/change_list.html'
    
    def display_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artists.all()[:3]])
    
    display_artists.short_description = 'Artists'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ticketmaster-sync/', self.admin_site.admin_view(self.ticketmaster_sync_view), 
                 name='ticketmaster_sync'),
            path('riviera-sync/', self.admin_site.admin_view(self.riviera_sync_view),
                 name='riviera_sync'),
            path('cafeberlin-sync/', self.admin_site.admin_view(self.cafeberlin_sync_view),
                 name='cafeberlin_sync'),
        ]
        return custom_urls + urls
    
    def ticketmaster_sync_view(self, request):
        if request.method == 'POST':
            form = TicketmasterSyncForm(request.POST)
            if form.is_valid():
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                created, updated, error = sync_events_for_city(city, state)
                if error:
                    self.message_user(request, f"Error syncing events: {error}", level=messages.ERROR)
                else:
                    self.message_user(request, f"Successfully synced events for {city}. Created: {created}, Updated: {updated}")
                return redirect('..')
        else:
            form = TicketmasterSyncForm()
        
        return render(request, 'admin/events/event/ticketmaster_sync.html', {'form': form})
    
    def riviera_sync_view(self, request):
        if request.method == 'POST':
            created, updated, error = sync_riviera_events()
            if error:
                self.message_user(request, f"Error syncing Riviera events: {error}", level=messages.ERROR)
            else:
                self.message_user(request, f"Successfully synced Riviera events. Created: {created}, Updated: {updated}")
            return redirect('..')
        
        return render(request, 'admin/events/event/riviera_sync.html', {})
    
    def cafeberlin_sync_view(self, request):
        if request.method == 'POST':
            created, updated, error = sync_cafeberlin_events()
            if error:
                self.message_user(request, f"Error syncing Cafe Berlin events: {error}", level=messages.ERROR)
            else:
                self.message_user(request, f"Successfully synced Cafe Berlin events. Created: {created}, Updated: {updated}")
            return redirect('..')
        
        return render(request, 'admin/events/event/cafeberlin_sync.html', {})


# Register with the default admin site
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Event, EventAdmin)

# Register with our custom admin site
admin_site.register(Artist, ArtistAdmin)
admin_site.register(Venue, VenueAdmin)
admin_site.register(Event, EventAdmin)