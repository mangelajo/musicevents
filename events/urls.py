from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>-<slug:slug>/', views.event_detail, name='event_detail'),
    path('artists/', views.ArtistListView.as_view(), name='artist_list'),
    path('artists/<int:pk>/', views.ArtistDetailView.as_view(), name='artist_detail'),
    path('venues/', views.VenueListView.as_view(), name='venue_list'),
    path('venues/<int:pk>/', views.VenueDetailView.as_view(), name='venue_detail'),
    
    # Ticketmaster sync views
    path('ticketmaster/sync/', staff_member_required(views.TicketmasterSyncView.as_view()), name='ticketmaster_sync'),
    path('ticketmaster/sync-func/', views.ticketmaster_sync_view, name='ticketmaster_sync_func'),
    
    # Sala Riviera sync views
    path('riviera/sync/', views.RivieraSyncView.as_view(), name='riviera_sync'),
    path('riviera/sync-func/', views.riviera_sync_view, name='riviera_sync_func'),
]