from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Equipment, Project, Inquiry, ThemeLine, Material, EquipmentVariant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_count', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_editable = ['is_active', 'order']
    
    def equipment_count(self, obj):
        return obj.equipment_count
    equipment_count.short_description = 'Equipment Count'

@admin.register(ThemeLine)
class ThemeLineAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class EquipmentVariantInline(admin.TabularInline):
    model = EquipmentVariant
    extra = 0
    readonly_fields = ('variant_name', 'dimensions', 'safety_zone', 'material', 'max_users')
    can_delete = False

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_number', 'category', 'theme_line', 'age_group', 'is_featured', 'is_active']
    list_filter = ['category', 'theme_line', 'age_group', 'safety_standard', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'model_number', 'description']
    prepopulated_fields = {}
    ordering = ['-is_featured', '-created_at']
    list_editable = ['is_featured', 'is_active']
    filter_horizontal = ['materials']
    inlines = [EquipmentVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'model_number', 'category', 'theme_line', 'description', 'suitable_for')
        }),
        ('Technical Specifications', {
            'fields': ('dimensions', 'safety_zone', 'max_users', 'age_group', 'materials', 'safety_standard', 'maintenance_level')
        }),
        ('Features & Status', {
            'fields': ('is_featured', 'is_active', 'foundation_required', 'installation_time', 'warranty_years')
        }),
        ('Images', {
            'fields': ('gallery_images',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'theme_line')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'project_type', 'location', 'client', 'is_featured', 'is_active', 'completion_date']
    list_filter = ['project_type', 'is_featured', 'is_active', 'completion_date']
    search_fields = ['title', 'description', 'location', 'client']
    ordering = ['-is_featured', '-completion_date']
    list_editable = ['is_featured', 'is_active']
    filter_horizontal = ['equipment_used']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'project_type', 'location', 'client')
        }),
        ('Project Details', {
            'fields': ('equipment_used', 'completion_date', 'project_duration', 'budget_range')
        }),
        ('Status & Images', {
            'fields': ('is_featured', 'is_active', 'main_image', 'gallery_images')
        }),
    )

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['contact_person', 'email', 'inquiry_type', 'equipment', 'is_read', 'is_responded', 'created_at']
    list_filter = ['inquiry_type', 'is_read', 'is_responded', 'created_at']
    search_fields = ['contact_person', 'email', 'company_name', 'message']
    ordering = ['-created_at']
    list_editable = ['is_read', 'is_responded']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('company_name', 'contact_person', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('inquiry_type', 'equipment', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'is_responded')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('equipment')
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected inquiries as read"
    
    def mark_as_responded(self, request, queryset):
        queryset.update(is_responded=True)
    mark_as_responded.short_description = "Mark selected inquiries as responded"
    
    actions = ['mark_as_read', 'mark_as_responded']

# Customize admin site
admin.site.site_header = "Playground Equipment Admin"
admin.site.site_title = "Equipment Catalog Admin"
admin.site.index_title = "Welcome to Playground Equipment Catalog Administration"
