from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.contrib import messages
from .models import Contribution, Gallery, ContributionCounter, Activity, Project
from .forms import ContributionForm
from django.utils import timezone
import calendar
from .models import District

# Create your views here.

class HomeView(TemplateView):
    template_name = 'web/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['counters'] = ContributionCounter.objects.all()
        return context

class ContributionCreateView(CreateView):
    model = Contribution
    form_class = ContributionForm
    template_name = 'web/contribution_form.html'
    success_url = None  # Remove the static success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contribution_type = self.kwargs.get('contribution_type', 'ZAKAH')
        context['contribution_type'] = contribution_type
        
        # Get contribution counter for the selected type
        counter, _ = ContributionCounter.objects.get_or_create(contribution_type=contribution_type)
        context['counter'] = counter

        # If this is a project contribution, get active projects
        if contribution_type == 'PROJECTS':
            context['active_projects'] = Project.objects.filter(is_active=True)
        
        return context

    def form_valid(self, form):
        # Set the contribution type from URL parameter
        form.instance.contribution_type = self.kwargs.get('contribution_type', 'ZAKAH')
        
        # Generate receipt number
        if not form.instance.receipt_number:
            prefix = form.instance.contribution_type[:3].upper()
            date_str = timezone.now().strftime('%y%m%d')
            last_receipt = Contribution.objects.filter(
                receipt_number__startswith=f'{prefix}{date_str}'
            ).order_by('-receipt_number').first()
            
            if last_receipt:
                last_num = int(last_receipt.receipt_number[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
                
            form.instance.receipt_number = f'{prefix}{date_str}{new_num:04d}'
        
        # Save the form and get the created contribution
        self.object = form.save()
        
        # Update contribution counter
        counter, _ = ContributionCounter.objects.get_or_create(
            contribution_type=form.instance.contribution_type
        )
        counter.count += 1
        counter.total_amount += form.instance.amount
        counter.save()
        
        # Redirect to the receipt page with the new contribution's ID
        return redirect('web:receipt', contribution_id=self.object.id)

    def get_initial(self):
        initial = super().get_initial()
        initial['contribution_type'] = self.kwargs.get('contribution_type')
        return initial

class ReceiptView(DetailView):
    model = Contribution
    template_name = 'web/receipt.html'
    context_object_name = 'contribution'

    def get_object(self):
        return get_object_or_404(Contribution, id=self.kwargs['contribution_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contribution = self.get_object()
        try:
            context['counter'] = ContributionCounter.objects.get(contribution_type=contribution.contribution_type)
        except ContributionCounter.DoesNotExist:
            context['counter'] = None
        return context

class GalleryView(ListView):
    model = Gallery
    template_name = 'web/gallery.html'
    context_object_name = 'gallery_items'
    ordering = ['-date_added']

class DashboardView(LoginRequiredMixin, ListView):
    model = Contribution
    template_name = 'web/dashboard.html'
    context_object_name = 'contributions'
    ordering = ['-date_contributed']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_contributions'] = Contribution.objects.count()
        context['total_amount'] = Contribution.objects.aggregate(total=Sum('amount'))['total']
        context['counters'] = ContributionCounter.objects.all()
        return context

class ContributionListView(ListView):
    model = Contribution
    template_name = 'web/contribution_list.html'
    context_object_name = 'contributions'

    def get_queryset(self):
        contribution_type = self.kwargs.get('contribution_type')
        return Contribution.objects.filter(contribution_type=contribution_type)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contribution_type = self.kwargs.get('contribution_type')
        context['contribution_type'] = contribution_type
        
        # Get or create the counter
        counter, created = ContributionCounter.objects.get_or_create(
            contribution_type=contribution_type,
            defaults={
                'count': 0,
                'total_amount': 0
            }
        )
        context['counter'] = counter
        
        return context

class OverallContributionsView(TemplateView):
    template_name = 'web/overall_contributions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get total contributions and amount
        total_contributions = Contribution.objects.count()
        total_amount = Contribution.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Get contribution type breakdown
        type_breakdown = []
        for type_code, type_name in Contribution.CONTRIBUTION_TYPES:
            contributions = Contribution.objects.filter(contribution_type=type_code)
            count = contributions.count()
            amount = contributions.aggregate(total=Sum('amount'))['total'] or 0
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            type_breakdown.append({
                'type': type_name,
                'count': count,
                'amount': amount,
                'percentage': round(percentage, 1)
            })
        
        # Get monthly breakdown
        monthly_data = []
        current_year = timezone.now().year
        for month in range(1, 13):
            contributions = Contribution.objects.filter(
                date_contributed__year=current_year,
                date_contributed__month=month
            )
            amount = contributions.aggregate(total=Sum('amount'))['total'] or 0
            monthly_data.append({
                'month': calendar.month_abbr[month],
                'amount': amount
            })
        
        context.update({
            'total_contributions': total_contributions,
            'total_amount': total_amount,
            'type_breakdown': type_breakdown,
            'monthly_data': monthly_data,
            'current_year': current_year
        })
  
        # Get all districts under all contributions, and then make total for each
        districts_with_contributions = []

        for district in District.objects.all():
            contributions = Contribution.objects.filter(district=district)
            total = contributions.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            districts_with_contributions.append({
                'district': district,
                'total_amount': total,
                'contributors_count': len(contributions), 
                'contributions': contributions,
            })

        context['district_data'] = districts_with_contributions
        
        return context

class OngoingProjectsView(TemplateView):
    template_name = 'web/ongoing_projects.html'

class ActivityListView(ListView):
    model = Activity
    template_name = 'web/activities.html'
    context_object_name = 'activities'

    def get_queryset(self):
        return Activity.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group activities by frequency
        grouped_activities = {
            'DAILY': [],
            'WEEKLY': [],
            'MONTHLY': [],
            'CUSTOM': []
        }
        for activity in self.get_queryset():
            grouped_activities[activity.frequency].append(activity)
        context['grouped_activities'] = grouped_activities
        return context

class ProjectListView(ListView):
    model = Project
    template_name = 'web/projects.html'
    context_object_name = 'projects'
    ordering = ['-created_at']

    def get_queryset(self):
        return Project.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here if needed
        return context
