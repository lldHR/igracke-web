from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.conf import settings

# Create your models here.
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'test_model'

class Category(models.Model):
    """Equipment categories like Street Workout, Ocean Themed, Jungle Themed, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-cube', help_text='FontAwesome icon class')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'pk': self.pk})

    @property
    def equipment_count(self):
        return self.equipment_set.filter(is_active=True).count()

class ThemeLine(models.Model):
    """Theme lines for equipment like City Line, Ocean Line, etc."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        db_table = 'catalog_theme_line'

    def __str__(self):
        return self.name

class Material(models.Model):
    """Materials used for equipment like Wood, Steel, etc."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        db_table = 'catalog_material'

    def __str__(self):
        return self.name

class EquipmentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = 'catalog_equipment_type'
        ordering = ['name']
    def __str__(self):
        return self.name

class Equipment(models.Model):
    """Playground and street workout equipment"""
    
    AGE_GROUP_CHOICES = [
        ('0-3 godine', '0-3 godine'),
        ('3-12 godina', '3-12 godina'),
        ('12-16 godina', '12-16 godina'),
        ('16+ godina', '16+ godina'),
    ]
    
    SAFETY_STANDARD_CHOICES = [
        ('en1176', 'EN 1176 (European)'),
        ('astm_f1487', 'ASTM F1487 (US)'),
        ('as4685', 'AS 4685 (Australian)'),
        ('csa_z614', 'CSA Z614 (Canadian)'),
        ('custom', 'Custom Standard'),
    ]
    
    MAINTENANCE_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    model_number = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    theme_line = models.ForeignKey(ThemeLine, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    suitable_for = models.TextField(help_text="Description of who this equipment is suitable for")
    
    # Technical Specifications
    dimensions = models.CharField(max_length=100, help_text="e.g., 3.5m x 2.8m x 2.1m")
    safety_zone = models.CharField(max_length=100, help_text="Required safety zone around equipment")
    max_users = models.PositiveIntegerField(default=1, help_text="Maximum simultaneous users")
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    materials = models.ManyToManyField(Material, blank=True, db_table='catalog_equipment_material')
    safety_standard = models.CharField(max_length=20, choices=SAFETY_STANDARD_CHOICES)
    maintenance_level = models.CharField(max_length=10, choices=MAINTENANCE_LEVEL_CHOICES)
    
    # Features
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    foundation_required = models.BooleanField(default=True)
    installation_time = models.CharField(max_length=50, help_text="e.g., 2-3 days")
    warranty_years = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(10)])
    has_variant = models.BooleanField(default=False)
    
    # Images
    gallery_images = models.JSONField(default=list, blank=True, help_text="Lista slika (prva slika se koristi kao glavna slika)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # New fields
    types = models.ManyToManyField(EquipmentType, blank=True, db_table='catalog_equipment_type_link')
    
    # Additional fields
    material = models.CharField(max_length=255, blank=True, null=True)
    dwg_files = models.JSONField(default=list, blank=True, help_text="Lista DWG datoteka (linkova)")
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name_plural = 'Equipment'
        unique_together = ('model_number', 'theme_line')

    def __str__(self):
        return f"{self.name} ({self.model_number})"

    def get_absolute_url(self):
        return reverse('catalog:equipment_detail', kwargs={'pk': self.pk})

    def get_age_group_display(self):
        return dict(self.AGE_GROUP_CHOICES).get(self.age_group, self.age_group)

    def get_materials_display(self):
        return ", ".join([mat.name for mat in self.materials.all()])

    def get_safety_standard_display(self):
        return dict(self.SAFETY_STANDARD_CHOICES).get(self.safety_standard, self.safety_standard)

    def get_maintenance_level_display(self):
        return dict(self.MAINTENANCE_LEVEL_CHOICES).get(self.maintenance_level, self.maintenance_level)

    def get_main_image_url(self):
        """Get the main image URL from gallery_images (first image)"""
        if self.gallery_images and len(self.gallery_images) > 0:
            return self.gallery_images[0]
        return None

    def get_public_image_url(self, image_path):
        """Generate public URL for image from object path"""
        if not image_path or not settings.SUPABASE_URL:
            return None
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_IMAGES_BUCKET}/{image_path}"

    def get_public_dwg_url(self, dwg_path):
        """Generate public URL for DWG file from object path"""
        if not dwg_path or not settings.SUPABASE_URL:
            return None
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_DWGS_BUCKET}/{dwg_path}"

    def get_main_image_public_url(self):
        """Get the main image public URL from gallery_images (first image)"""
        if self.gallery_images and len(self.gallery_images) > 0:
            return self.get_public_image_url(self.gallery_images[0])
        return None

    def get_gallery_images_public_urls(self):
        """Get all gallery images as public URLs"""
        if not self.gallery_images:
            return []
        return [self.get_public_image_url(img_path) for img_path in self.gallery_images]

    def get_dwg_files_public_urls(self):
        """Get all DWG files as public URLs"""
        if not self.dwg_files:
            return []
        return [self.get_public_dwg_url(dwg_path) for dwg_path in self.dwg_files]

class Inquiry(models.Model):
    """Customer inquiries about equipment"""
    
    INQUIRY_TYPE_CHOICES = [
        ('quote', 'Request Quote'),
        ('info', 'Request Information'),
        ('consultation', 'Request Consultation'),
        ('installation', 'Installation Inquiry'),
        ('maintenance', 'Maintenance Inquiry'),
        ('other', 'Other'),
    ]
    
    # Contact Information
    company_name = models.CharField(max_length=200, blank=True)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Inquiry Details
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPE_CHOICES)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry from {self.contact_person} - {self.get_inquiry_type_display()}"

    def get_inquiry_type_display(self):
        return dict(self.INQUIRY_TYPE_CHOICES).get(self.inquiry_type, self.inquiry_type)

class Project(models.Model):
    """Showcase projects/installations"""
    
    PROJECT_TYPE_CHOICES = [
        ('playground', 'Playground'),
        ('street_workout', 'Street Workout'),
        ('fitness_park', 'Fitness Park'),
        ('school', 'School'),
        ('park', 'Public Park'),
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    client = models.CharField(max_length=200, blank=True)
    
    # Equipment used
    equipment_used = models.ManyToManyField(Equipment, blank=True)
    
    # Project details
    completion_date = models.DateField(blank=True, null=True)
    project_duration = models.CharField(max_length=50, blank=True, help_text="e.g., 3 weeks")
    budget_range = models.CharField(max_length=50, blank=True, help_text="e.g., €50,000 - €75,000")
    
    # Images
    main_image = models.ImageField(upload_to='projects/', blank=True, null=True)
    gallery_images = models.JSONField(default=list, blank=True)
    
    # Features
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-completion_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})

    def get_project_type_display(self):
        return dict(self.PROJECT_TYPE_CHOICES).get(self.project_type, self.project_type)

class EquipmentVariant(models.Model):
    equipment = models.ForeignKey('Equipment', related_name='variants', on_delete=models.CASCADE, db_column='equipment_id')
    variant_name = models.CharField(max_length=100, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    safety_zone = models.CharField(max_length=100, blank=True, null=True)
    material = models.ForeignKey('Material', null=True, blank=True, on_delete=models.SET_NULL, db_column='material_id')
    max_users = models.IntegerField(blank=True, null=True)
    theme_line = models.ForeignKey('ThemeLine', null=True, blank=True, on_delete=models.SET_NULL, db_column='theme_line_id')
    materials = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'catalog_equipment_variant'

    def __str__(self):
        return self.variant_name or f"Varijanta za {self.equipment}"
