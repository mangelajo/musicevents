from django.urls import path
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
    

]