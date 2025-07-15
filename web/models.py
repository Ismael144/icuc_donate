from django.db import models
from django.db.models import Sum
from django.utils import timezone

class Contribution(models.Model):
    CONTRIBUTION_TYPES = [
        ('ZAKAH', 'Zakah'),
        ('SADAQA', 'Sadaqa'),
        ('FITRA', 'Fitra'),
        ('OTHER', 'Other'),
    ]

    ZAKAH_TYPES = [
        ('MAAL', 'Zakah al-Maal'),
        ('FITRI', 'Zakah al-Fitr'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    contribution_type = models.CharField(max_length=10, choices=CONTRIBUTION_TYPES)
    zakah_type = models.CharField(max_length=5, choices=ZAKAH_TYPES, null=True, blank=True)
    number_of_people = models.PositiveIntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_contributed = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=20, unique=True, blank=True)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_contribution_type_display()} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number
            prefix = self.contribution_type[:3].upper()
            date_str = self.date_contributed.strftime('%y%m%d')
            last_receipt = Contribution.objects.filter(
                receipt_number__startswith=f'{prefix}{date_str}'
            ).order_by('-receipt_number').first()
            
            if last_receipt:
                last_num = int(last_receipt.receipt_number[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
                
            self.receipt_number = f'{prefix}{date_str}{new_num:04d}'
        
        super().save(*args, **kwargs)
        
        # Update project current amount if this is a project contribution
        if self.contribution_type == 'PROJECTS' and self.project:
            self.project.current_amount += self.amount
            self.project.save()


class District(models.Model): 
    name = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_created=True)

    def __str__(self): 
        return self.name

    def contributions(self):
        return self.contribution_set.all()

    def total_amount(self):
        return self.contribution_set.aggregate(total=Sum('amount'))['total'] or 0


class Gallery(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='gallery/')
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ContributionCounter(models.Model):
    contribution_type = models.CharField(max_length=10, choices=Contribution.CONTRIBUTION_TYPES, unique=True)
    count = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.contribution_type} - {self.count} contributions"

class Activity(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('CUSTOM', 'Custom Schedule')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class name (e.g., 'bi-book')")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    schedule_details = models.CharField(max_length=200, help_text="E.g., 'Every Saturday' or 'First Monday of the month'")
    time = models.CharField(max_length=100, help_text="E.g., '9:00 AM - 12:00 PM'")
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['frequency', 'schedule_details']

    def __str__(self):
        return self.title

class Project(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Coming Soon'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=0)
    current_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ONGOING')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return round((self.current_amount / self.target_amount) * 100, 1)
        return 0

    @property
    def supporter_count(self):
        return Contribution.objects.filter(
            contribution_type='PROJECTS',
            project=self
        ).count()

    class Meta:
        ordering = ['-created_at']

class ZakahNisab(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='KES')
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Zakah Nisab'
        verbose_name_plural = 'Zakah Nisab'

    def save(self, *args, **kwargs):
        if self.is_active:
            # Set all other records to inactive
            ZakahNisab.objects.all().update(is_active=False)
            self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.currency} {self.amount:,.2f} (Updated: {self.last_updated.strftime('%Y-%m-%d')})"
