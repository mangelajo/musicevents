from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, View
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
from django import forms
from .models import Artist, Venue, Event
from .utils.ticketmaster import sync_events_for_city
from .utils.riviera_sync import sync_riviera_events

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
    
    def get_queryset(self):
        queryset = Event.objects.filter(date__gte=timezone.now()).order_by('date')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

class VenueDetailView(DetailView):
    model = Venue
    template_name = 'events/venue_detail.html'
    context_object_name = 'venue'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = self.object.events.filter(date__gte=timezone.now()).order_by('date')
        context['past_events'] = self.object.events.filter(date__lt=timezone.now()).order_by('-date')
        return context


class TicketmasterSyncForm(forms.Form):
    city = forms.CharField(max_length=100, required=True, help_text="Enter city name (e.g., 'New York')")
    state = forms.CharField(max_length=2, required=False, help_text="Enter state code (e.g., 'NY')")


class TicketmasterSyncView(FormView):
    template_name = 'events/ticketmaster_sync.html'
    form_class = TicketmasterSyncForm
    success_url = reverse_lazy('events:event_list')
    
    def form_valid(self, form):
        city = form.cleaned_data['city']
        state = form.cleaned_data['state']
        
        created, updated, error = sync_events_for_city(city, state)
        
        if error:
            messages.error(self.request, f"Error syncing events: {error}")
        else:
            messages.success(self.request, f"Successfully synced events for {city}. Created: {created}, Updated: {updated}")
        
        return super().form_valid(form)


@user_passes_test(lambda u: u.is_staff)
def ticketmaster_sync_view(request):
    if request.method == 'POST':
        form = TicketmasterSyncForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            
            created, updated, error = sync_events_for_city(city, state)
            
            if error:
                messages.error(request, f"Error syncing events: {error}")
            else:
                messages.success(request, f"Successfully synced events for {city}. Created: {created}, Updated: {updated}")
            
            return redirect('events:event_list')
    else:
        form = TicketmasterSyncForm()
    
    return render(request, 'events/ticketmaster_sync.html', {'form': form})


class RivieraSyncView(View):
    """View for synchronizing events from Sala Riviera website."""
    
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return user_passes_test(lambda u: u.is_staff)(view)
    
    def get(self, request):
        return render(request, 'events/riviera_sync.html')
    
    def post(self, request):
        created, updated, errors = sync_riviera_events()
        
        if errors > 0:
            messages.warning(request, f"Synchronized Sala Riviera events with {errors} errors. Created: {created}, Updated: {updated}")
        else:
            messages.success(request, f"Successfully synchronized Sala Riviera events. Created: {created}, Updated: {updated}")
        
        return redirect('events:event_list')


@user_passes_test(lambda u: u.is_staff)
def riviera_sync_view(request):
    """Function-based view for synchronizing events from Sala Riviera website."""
    if request.method == 'POST':
        created, updated, errors = sync_riviera_events()
        
        if errors > 0:
            messages.warning(request, f"Synchronized Sala Riviera events with {errors} errors. Created: {created}, Updated: {updated}")
        else:
            messages.success(request, f"Successfully synchronized Sala Riviera events. Created: {created}, Updated: {updated}")
        
        return redirect('events:event_list')
    
    return render(request, 'events/riviera_sync.html')
