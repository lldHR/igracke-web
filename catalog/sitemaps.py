from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Equipment, Category, Project

class EquipmentSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Equipment.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.filter(is_active=True)

class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.filter(is_active=True)

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ['catalog:home', 'catalog:about', 'catalog:contact', 'catalog:equipment_list', 'catalog:projects_list']

    def location(self, item):
        return reverse(item)
