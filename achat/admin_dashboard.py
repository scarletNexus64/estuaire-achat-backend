from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import CustomUser, Location, UserToken, Category, SubCategory


@method_decorator(staff_member_required, name='dispatch')
class AchatDashboardView(TemplateView):
    template_name = 'admin/achat/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date for calculations
        now = datetime.now()
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        
        # User statistics
        total_users = CustomUser.objects.count()
        new_users_week = CustomUser.objects.filter(date_joined__gte=last_week).count()
        new_users_month = CustomUser.objects.filter(date_joined__gte=last_month).count()
        active_tokens = UserToken.objects.count()
        
        # Gender distribution
        gender_stats = CustomUser.objects.values('gender').annotate(count=Count('gender'))
        
        # Location statistics
        total_locations = Location.objects.count()
        default_locations = Location.objects.filter(is_default=True).count()
        top_cities = Location.objects.values('name').annotate(
            count=Count('name')
        ).order_by('-count')[:5]
        
        # Category statistics
        total_categories = Category.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()
        total_subcategories = SubCategory.objects.count()
        active_subcategories = SubCategory.objects.filter(is_active=True).count()
        
        # Recent activity
        recent_users = CustomUser.objects.order_by('-date_joined')[:5]
        recent_locations = Location.objects.order_by('-created_at')[:5]
        recent_categories = Category.objects.order_by('-created_at')[:5]
        recent_subcategories = SubCategory.objects.order_by('-created_at')[:5]
        
        context.update({
            # User metrics
            'total_users': total_users,
            'new_users_week': new_users_week,
            'new_users_month': new_users_month,
            'active_tokens': active_tokens,
            
            # Gender distribution
            'gender_stats': gender_stats,
            
            # Location metrics
            'total_locations': total_locations,
            'default_locations': default_locations,
            'top_cities': top_cities,
            
            # Category metrics
            'total_categories': total_categories,
            'active_categories': active_categories,
            'total_subcategories': total_subcategories,
            'active_subcategories': active_subcategories,
            
            # Recent activity
            'recent_users': recent_users,
            'recent_locations': recent_locations,
            'recent_categories': recent_categories,
            'recent_subcategories': recent_subcategories,
            
            # Growth percentages (mock data for now)
            'user_growth': round((new_users_month / max(total_users - new_users_month, 1)) * 100, 1),
            'location_growth': round((total_locations / max(total_users, 1)) * 100, 1),
            
            # System info
            'dashboard_title': '📊 Dashboard Achat - ESTUAIRE',
            'last_updated': now,
        })
        
        return context


def achat_dashboard_view(request):
    """
    Function-based view for the dashboard
    """
    if not request.user.is_staff:
        return admin.site.admin_view(lambda r: None)(request)
    
    view = AchatDashboardView()
    view.request = request
    return view.get(request)