from django.contrib import admin
from .models import Contribution, Gallery, ContributionCounter, Activity, Project, ZakahNisab, District

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'contribution_type', 'amount', 'date_contributed', 'receipt_number')
    list_filter = ('contribution_type', 'date_contributed')
    search_fields = ('first_name', 'last_name', 'phone_number', 'receipt_number')
    readonly_fields = ('receipt_number', 'date_contributed')
    ordering = ('-date_contributed',)

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added')
    search_fields = ('title', 'description')
    list_filter = ('date_added',)
    
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin): 
    list_display = ('name', 'date_created')

@admin.register(ContributionCounter)
class ContributionCounterAdmin(admin.ModelAdmin):
    list_display = ('contribution_type', 'count', 'total_amount')
    readonly_fields = ('count', 'total_amount')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'frequency', 'schedule_details', 'time', 'location', 'is_active')
    list_filter = ('frequency', 'is_active')
    search_fields = ('title', 'description', 'location')
    ordering = ('frequency', 'schedule_details')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'target_amount', 'current_amount', 'progress_percentage', 'supporter_count', 'is_active')
    list_filter = ('status', 'is_active')
    search_fields = ('title', 'description')
    readonly_fields = ('current_amount', 'progress_percentage', 'supporter_count')
    ordering = ('-created_at',)

@admin.register(ZakahNisab)
class ZakahNisabAdmin(admin.ModelAdmin):
    list_display = ('amount', 'currency', 'last_updated', 'is_active')
    readonly_fields = ('last_updated',)
    list_filter = ('is_active', 'currency')
    ordering = ('-last_updated',)
