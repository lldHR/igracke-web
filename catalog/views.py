from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from django.urls import reverse
from .models import Category, Equipment, Project, Inquiry, ThemeLine, Material, EquipmentType

from django.views.decorators.cache import cache_page

# @cache_page(60 * 15)  # Temporarily disabled for debugging
def home(request):
    """Home page with featured equipment and categories"""
    featured_equipment = Equipment.objects.filter(is_featured=True, is_active=True)[:6]
    categories = Category.objects.filter(is_active=True).annotate(active_equipment_count=Count('equipment', filter=Q(equipment__is_active=True)))[:8]
    featured_projects = Project.objects.filter(is_featured=True, is_active=True)[:3]
    
    context = {
        'featured_equipment': featured_equipment,
        'categories': categories,
        'featured_projects': featured_projects,
    }
    return render(request, 'catalog/home.html', context)

def equipment_list(request):
    """Equipment catalog with search and filters"""
    equipment_list = Equipment.objects.filter(is_active=True).select_related('category', 'theme_line').prefetch_related('materials', 'types')
    
    # Get filter parameters from URL
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category')
    theme_id = request.GET.get('theme_line')
    material_id = request.GET.get('material')
    age_filter = request.GET.get('age_group', '')
    safety_filter = request.GET.get('safety_standard', '')
    featured_only = request.GET.get('featured_only') == 'on'
    sort_by = request.GET.get('sort', '')
    type_ids = request.GET.getlist('type')
    
    if search_query:
        equipment_list = equipment_list.filter(
            Q(name__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_id:
        equipment_list = equipment_list.filter(category_id=category_id)
        
    if theme_id:
        equipment_list = equipment_list.filter(theme_line_id=theme_id)
        
    if material_id:
        equipment_list = equipment_list.filter(materials=material_id)
    
    if age_filter:
        equipment_list = equipment_list.filter(age_group=age_filter)
    
    if safety_filter:
        equipment_list = equipment_list.filter(safety_standard=safety_filter)
    
    if featured_only:
        equipment_list = equipment_list.filter(is_featured=True)
    
    if type_ids:
        equipment_list = equipment_list.filter(types__id__in=type_ids)
    
    # Apply sorting
    if sort_by == 'name':
        equipment_list = equipment_list.order_by('name')
    elif sort_by == 'featured':
        equipment_list = equipment_list.order_by('-is_featured', '-created_at')
    elif sort_by == 'newest':
        equipment_list = equipment_list.order_by('-created_at')
    else:
        equipment_list = equipment_list.order_by('-is_featured', '-created_at')

    # Pagination
    paginator = Paginator(equipment_list.distinct(), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Compute visible page range (up to 5 pages centered on current)
    current_page = page_obj.number
    total_pages = paginator.num_pages
    half_window = 2
    start_page = max(1, current_page - half_window)
    end_page = min(total_pages, current_page + half_window)
    if end_page - start_page < 4 and total_pages >= 5:
        if start_page == 1:
            end_page = min(5, total_pages)
        elif end_page == total_pages:
            start_page = max(1, total_pages - 4)
    page_range = range(start_page, end_page + 1)
    
    # Get filter options for template
    categories = Category.objects.filter(is_active=True)
    theme_lines = ThemeLine.objects.all()
    materials = Material.objects.all()
    types = EquipmentType.objects.all()
    
    context = {
        'page_obj': page_obj,
        'page_range': page_range,
        'categories': categories,
        'theme_lines': theme_lines,
        'materials': materials,
        'types': types,
        'age_choices': Equipment.AGE_GROUP_CHOICES,
        'safety_choices': Equipment.SAFETY_STANDARD_CHOICES,
        'current_filters': {
            'search': search_query,
            'category': category_id,
            'theme_line': theme_id,
            'material': material_id,
            'age_group': age_filter,
            'safety_standard': safety_filter,
            'featured_only': featured_only,
            'sort': sort_by,
            'type': type_ids,
        }
    }
    return render(request, 'catalog/equipment_list.html', context)

def equipment_detail(request, pk):
    """Detailed view of equipment"""
    equipment = get_object_or_404(Equipment, pk=pk, is_active=True)
    related_equipment = Equipment.objects.filter(
        category=equipment.category,
        is_active=True
    ).exclude(pk=equipment.pk)[:3]
    variants = equipment.variants.all() if equipment.has_variant else []
    # Extra gallery images (skip the first one, it's the main image)
    extra_images = []
    if equipment.gallery_images and len(equipment.gallery_images) > 1:
        extra_images = [equipment.get_public_image_url(img) for img in equipment.gallery_images[1:]]
    context = {
        'equipment': equipment,
        'related_equipment': related_equipment,
        'variants': variants,
        'extra_images': extra_images,
    }
    return render(request, 'catalog/equipment_detail.html', context)

def category_detail(request, pk):
    """Category detail page showing all equipment in a category"""
    category = get_object_or_404(Category, pk=pk, is_active=True)
    equipment_list = Equipment.objects.filter(category=category, is_active=True)
    
    # Apply filters
    search_query = request.GET.get('search', '')
    age_filter = request.GET.get('age', '')
    material_filter = request.GET.get('material', '')
    
    if search_query:
        equipment_list = equipment_list.filter(
            Q(name__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if age_filter:
        equipment_list = equipment_list.filter(age_group=age_filter)
    
    if material_filter:
        equipment_list = equipment_list.filter(material=material_filter)
    
    # Pagination
    paginator = Paginator(equipment_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'search_query': search_query,
        'age_filter': age_filter,
        'material_filter': material_filter,
        'age_choices': Equipment.AGE_GROUP_CHOICES,
        'materials': Material.objects.all(),
    }
    return render(request, 'catalog/category_detail.html', context)

@cache_page(60 * 15)
def projects_list(request):
    """Showcase projects list"""
    projects_list = Project.objects.filter(is_active=True)
    
    # Filter by project type
    project_type = request.GET.get('type', '')
    if project_type:
        projects_list = projects_list.filter(project_type=project_type)
    
    # Pagination
    paginator = Paginator(projects_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'project_type': project_type,
        'project_types': Project.PROJECT_TYPE_CHOICES,
    }
    return render(request, 'catalog/projects_list.html', context)

def project_detail(request, pk):
    """Detailed view of a project"""
    project = get_object_or_404(Project, pk=pk, is_active=True)
    
    # Get related projects
    related_projects = Project.objects.filter(
        project_type=project.project_type,
        is_active=True
    ).exclude(pk=project.pk)[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'catalog/project_detail.html', context)

@cache_page(60 * 60)
def contact(request):
    """Contact page"""
    equipment_id = request.GET.get('equipment')
    equipment = None
    
    if equipment_id:
        try:
            equipment = Equipment.objects.get(pk=equipment_id, is_active=True)
        except Equipment.DoesNotExist:
            pass
    
    context = {
        'equipment': equipment,
    }
    return render(request, 'catalog/contact.html', context)

@cache_page(60 * 60)
def about(request):
    """About page"""
    return render(request, 'catalog/about.html')

def database_stats(request):
    """Database statistics for admin purposes"""
    stats = {
        'total_equipment': Equipment.objects.filter(is_active=True).count(),
        'featured_equipment': Equipment.objects.filter(is_featured=True, is_active=True).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_projects': Project.objects.filter(is_active=True).count(),
        'total_inquiries': Inquiry.objects.count(),
        'unread_inquiries': Inquiry.objects.filter(is_read=False).count(),
    }
    
    # Category breakdown
    categories = Category.objects.filter(is_active=True)
    category_stats = []
    for category in categories:
        category_stats.append({
            'name': category.name,
            'count': category.equipment_set.filter(is_active=True).count(),
        })
    
    context = {
        'stats': stats,
        'category_stats': category_stats,
    }
    return render(request, 'catalog/database_stats.html', context)
