from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import timezone
from .models import Artist, Venue, Event

def home(request):
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')[:5]
    featured_artists = Artist.objects.all()[:3]
    featured_venues = Venue.objects.all()[:3]
    
    context = {
        'upcoming_events': upcoming_events,
        'featured_artists': featured_artists,
        'featured_venues': featured_venues,
    }
    
    return render(request, 'events/home.html', context)

class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 9  # Show 9 events per page (3 rows of 3 events)
    
    def get_queryset(self):
        queryset = Event.objects.filter(date__gte=timezone.now()).order_by('date')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get past events separately (not paginated)
        context['past_events'] = Event.objects.filter(date__lt=timezone.now()).order_by('-date')[:5]
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_object(self, queryset=None):
        return get_object_or_404(Event, pk=self.kwargs['pk'], slug=self.kwargs['slug'])

def event_detail(request, pk, slug):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})

class ArtistListView(ListView):
    model = Artist
    template_name = 'events/artist_list.html'
    context_object_name = 'artists'
    paginate_by = 12  # Show 12 artists per page
    
    def get_queryset(self):
        return Artist.objects.all().order_by('name')

class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'events/artist_detail.html'
    context_object_name = 'artist'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = self.object.events.filter(date__gte=timezone.now()).order_by('date')
        context['past_events'] = self.object.events.filter(date__lt=timezone.now()).order_by('-date')
        return context

class VenueListView(ListView):
    model = Venue
    template_name = 'events/venue_list.html'
    context_object_name = 'venues'
    paginate_by = 12  # Show 12 venues per page
    
    def get_queryset(self):
        return Venue.objects.all().order_by('name')

class VenueDetailView(DetailView):
    model = Venue
    template_name = 'events/venue_detail.html'
    context_object_name = 'venue'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = self.object.events.filter(date__gte=timezone.now()).order_by('date')
        context['past_events'] = self.object.events.filter(date__lt=timezone.now()).order_by('-date')
        return context


class TermsView(TemplateView):
    """View for the terms and conditions page."""
    template_name = 'events/terms.html'

