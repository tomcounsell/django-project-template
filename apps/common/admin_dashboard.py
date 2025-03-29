"""
Custom admin dashboard for the Django project template.
"""
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.timezone import now

from apps.common.models import Team, TodoItem, Email, SMS, Payment, Subscription, Upload
from apps.common.admin import MAIN_NAV_MODELS, ADMIN_CATEGORIES

User = get_user_model()


def get_admin_dashboard(request, context=None):
    """
    Generate dashboard widgets and stats for the admin index page.
    
    This function is called by Django Unfold to customize the admin dashboard.
    
    Args:
        request: The current request object
        context: The current context dictionary
        
    Returns:
        Modified context with dashboard widgets
    """
    # Initialize context if not provided
    if context is None:
        context = {}
    
    # Only show dashboard for staff users
    if not request.user.is_staff:
        return context
    
    # Get model counts with more comprehensive stats
    # User statistics
    user_count = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    superusers = User.objects.filter(is_superuser=True).count()
    
    # Make sure we use a timezone-aware datetime
    today = now().date()
    recent_users = User.objects.filter(date_joined__date=today).count()
    
    # Team statistics
    team_count = Team.objects.count()
    active_teams = Team.objects.filter(is_active=True).count()
    teams_with_members = Team.objects.annotate(member_count=Count('members'))
    
    # Safe calculation of average team size
    if team_count > 0:
        avg_team_size = teams_with_members.aggregate(avg=Sum('member_count')).get('avg', 0) / team_count
    else:
        avg_team_size = 0
        
    largest_team = teams_with_members.order_by('-member_count').first()
    
    # Todo statistics
    todo_count = TodoItem.objects.count()
    todo_stats = {
        'TODO': TodoItem.objects.filter(status='TODO').count(),
        'IN_PROGRESS': TodoItem.objects.filter(status='IN_PROGRESS').count(),
        'BLOCKED': TodoItem.objects.filter(status='BLOCKED').count(),
        'DONE': TodoItem.objects.filter(status='DONE').count(),
    }
    overdue_todos = TodoItem.objects.filter(due_at__lt=now(), status__in=['TODO', 'IN_PROGRESS', 'BLOCKED']).count()
    
    # Communications
    email_count = Email.objects.count()
    unsent_emails = Email.objects.filter(sent_at__isnull=True).count()
    read_emails = Email.objects.filter(read_at__isnull=False).count()
    
    sms_count = SMS.objects.count()
    successful_sms = SMS.objects.filter(status='delivered').count()
    failed_sms = SMS.objects.filter(status='failed').count()
    
    # Finance 
    payment_count = Payment.objects.count()
    payment_stats = {
        'succeeded': Payment.objects.filter(status='succeeded').count(),
        'pending': Payment.objects.filter(status='pending').count(),
        'failed': Payment.objects.filter(status='failed').count(),
        'refunded': Payment.objects.filter(status='refunded').count(),
    }
    
    # Get total revenue with a fallback to 0 if None
    total_revenue_result = Payment.objects.filter(status='succeeded').aggregate(total=Sum('amount'))
    total_revenue = total_revenue_result.get('total') or 0
    
    subscription_count = Subscription.objects.count()
    subscription_stats = {
        'active': Subscription.objects.filter(status='active').count(),
        'trialing': Subscription.objects.filter(status='trialing').count(),
        'past_due': Subscription.objects.filter(status='past_due').count(),
        'canceled': Subscription.objects.filter(status='canceled').count(),
    }
    
    # Create rich, interactive dashboard widgets using advanced formatting
    widgets = [
        {
            "title": _("Dashboard"),
            "widgets": [
                # Users Widget with enhanced stats
                {
                    "title": _("Users"),
                    "content": f"""
                        <div class="p-4">
                            <div class="flex justify-between items-center mb-4">
                                <div>
                                    <div class="text-3xl font-bold">{user_count}</div>
                                    <div class="text-sm text-gray-500">Total Users</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-lg font-semibold text-green-600">+{recent_users} today</div>
                                    <div class="text-sm text-gray-500">{active_users} active ({active_users/user_count*100:.1f}%)</div>
                                </div>
                            </div>
                            
                            <div class="mt-4 grid grid-cols-3 gap-4">
                                <div class="bg-gray-100 dark:bg-gray-800 p-2 rounded">
                                    <div class="text-center font-semibold">{active_users}</div>
                                    <div class="text-center text-xs text-gray-600 dark:text-gray-400">Active</div>
                                </div>
                                <div class="bg-gray-100 dark:bg-gray-800 p-2 rounded">
                                    <div class="text-center font-semibold">{staff_users}</div>
                                    <div class="text-center text-xs text-gray-600 dark:text-gray-400">Staff</div>
                                </div>
                                <div class="bg-gray-100 dark:bg-gray-800 p-2 rounded">
                                    <div class="text-center font-semibold">{superusers}</div>
                                    <div class="text-center text-xs text-gray-600 dark:text-gray-400">Superusers</div>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <a href="{reverse('admin:common_user_changelist')}" 
                                   class="inline-flex items-center px-3 py-1 border border-transparent text-sm rounded-md 
                                   text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 
                                   focus:ring-offset-2 focus:ring-blue-500">
                                    <span class="material-symbols-outlined mr-1">person</span>
                                    Manage Users
                                </a>
                                <a href="{reverse('admin:auth_group_changelist')}" 
                                   class="ml-2 inline-flex items-center px-3 py-1 border border-gray-300 text-sm 
                                   rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none 
                                   focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <span class="material-symbols-outlined mr-1">groups</span>
                                    Groups
                                </a>
                            </div>
                        </div>
                    """,
                    "column": 1,
                    "order": 0,
                },
                
                # Teams Widget with enhanced stats
                {
                    "title": _("Teams"),
                    "content": f"""
                        <div class="p-4">
                            <div class="flex justify-between items-center mb-4">
                                <div>
                                    <div class="text-3xl font-bold">{team_count}</div>
                                    <div class="text-sm text-gray-500">Total Teams</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-lg font-semibold">{active_teams} active</div>
                                    <div class="text-sm text-gray-500">avg {avg_team_size:.1f} members/team</div>
                                </div>
                            </div>
                            
                            <div class="mt-3 mb-2 text-sm font-medium">Largest Team</div>
                            {f'<div class="bg-gray-100 dark:bg-gray-800 p-2 rounded mb-4"><div class="font-semibold">{largest_team.name}</div><div class="text-xs text-gray-600 dark:text-gray-400">{largest_team.member_count} members</div></div>' if largest_team else '<div class="text-gray-500 mb-4">No teams with members</div>'}
                            
                            <div class="flex justify-between">
                                <div class="">
                                    <div class="text-sm font-semibold">{active_teams}</div>
                                    <div class="text-xs text-gray-600 dark:text-gray-400">Active</div>
                                </div>
                                <div class="">
                                    <div class="text-sm font-semibold">{team_count - active_teams}</div>
                                    <div class="text-xs text-gray-600 dark:text-gray-400">Inactive</div>
                                </div>
                                <div class="">
                                    <div class="text-sm font-semibold">{teams_with_members.count()}</div>
                                    <div class="text-xs text-gray-600 dark:text-gray-400">With Members</div>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <a href="{reverse('admin:common_team_changelist')}" 
                                   class="inline-flex items-center px-3 py-1 border border-transparent text-sm rounded-md 
                                   text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 
                                   focus:ring-offset-2 focus:ring-blue-500">
                                    <span class="material-symbols-outlined mr-1">groups</span>
                                    Manage Teams
                                </a>
                                <a href="{reverse('admin:common_teammember_changelist')}" 
                                   class="ml-2 inline-flex items-center px-3 py-1 border border-gray-300 text-sm 
                                   rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none 
                                   focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <span class="material-symbols-outlined mr-1">person_add</span>
                                    Manage Members
                                </a>
                            </div>
                        </div>
                    """,
                    "column": 1,
                    "order": 1,
                },
                
                # Todo Widget with status breakdown
                {
                    "title": _("Todo Items"),
                    "content": f"""
                        <div class="p-4">
                            <div class="flex justify-between items-center mb-4">
                                <div>
                                    <div class="text-3xl font-bold">{todo_count}</div>
                                    <div class="text-sm text-gray-500">Total Todos</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-lg font-semibold text-amber-600">{todo_stats['TODO'] + todo_stats['IN_PROGRESS'] + todo_stats['BLOCKED']} active</div>
                                    <div class="text-sm text-red-500">{overdue_todos} overdue</div>
                                </div>
                            </div>
                            
                            <div class="mt-4 grid grid-cols-4 gap-2">
                                <div class="bg-blue-100 p-2 rounded text-center">
                                    <div class="font-semibold text-blue-800">{todo_stats['TODO']}</div>
                                    <div class="text-xs text-blue-800">Todo</div>
                                </div>
                                <div class="bg-yellow-100 p-2 rounded text-center">
                                    <div class="font-semibold text-yellow-800">{todo_stats['IN_PROGRESS']}</div>
                                    <div class="text-xs text-yellow-800">In Progress</div>
                                </div>
                                <div class="bg-red-100 p-2 rounded text-center">
                                    <div class="font-semibold text-red-800">{todo_stats['BLOCKED']}</div>
                                    <div class="text-xs text-red-800">Blocked</div>
                                </div>
                                <div class="bg-green-100 p-2 rounded text-center">
                                    <div class="font-semibold text-green-800">{todo_stats['DONE']}</div>
                                    <div class="text-xs text-green-800">Done</div>
                                </div>
                            </div>
                            
                            <div class="mt-4 flex items-center justify-between">
                                <div class="w-full bg-gray-200 rounded-full h-2.5">
                                    <div class="bg-blue-600 h-2.5 rounded-full" style="width: {todo_stats['DONE']/max(todo_count, 1)*100}%"></div>
                                </div>
                                <div class="ml-2 text-xs text-gray-500">{todo_stats['DONE']/max(todo_count, 1)*100:.1f}%</div>
                            </div>
                            
                            <div class="mt-4">
                                <a href="{reverse('admin:common_todoitem_changelist')}" 
                                   class="inline-flex items-center px-3 py-1 border border-transparent text-sm rounded-md 
                                   text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 
                                   focus:ring-offset-2 focus:ring-blue-500">
                                    <span class="material-symbols-outlined mr-1">check_box</span>
                                    Manage Todos
                                </a>
                                <a href="{reverse('admin:common_todoitem_changelist')}?status=TODO" 
                                   class="ml-2 inline-flex items-center px-3 py-1 border border-gray-300 text-sm 
                                   rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none 
                                   focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <span class="material-symbols-outlined mr-1">filter_list</span>
                                    View Pending
                                </a>
                            </div>
                        </div>
                    """,
                    "column": 1,
                    "order": 2,
                },
                
                # Communications Widget
                {
                    "title": _("Communications"),
                    "content": f"""
                        <div class="p-4">
                            <div class="grid grid-cols-2 gap-6">
                                <div class="border-r pr-5">
                                    <div class="flex items-baseline">
                                        <span class="material-symbols-outlined mr-2 text-blue-500">email</span>
                                        <div class="text-2xl font-bold">{email_count}</div>
                                    </div>
                                    <div class="text-sm text-gray-500 mb-3">Total Emails</div>
                                    
                                    <div class="space-y-2">
                                        <div class="flex justify-between text-sm">
                                            <span>Sent:</span>
                                            <span class="font-medium">{email_count - unsent_emails}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span>Pending:</span>
                                            <span class="font-medium">{unsent_emails}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span>Read:</span>
                                            <span class="font-medium">{read_emails}</span>
                                        </div>
                                    </div>
                                    
                                    <div class="mt-3">
                                        <a href="{reverse('admin:common_email_changelist')}" 
                                           class="text-blue-500 hover:text-blue-700 text-sm flex items-center">
                                            View all emails
                                            <span class="material-symbols-outlined ml-1 text-base">chevron_right</span>
                                        </a>
                                    </div>
                                </div>
                                
                                <div class="">
                                    <div class="flex items-baseline">
                                        <span class="material-symbols-outlined mr-2 text-green-500">sms</span>
                                        <div class="text-2xl font-bold">{sms_count}</div>
                                    </div>
                                    <div class="text-sm text-gray-500 mb-3">Total SMS</div>
                                    
                                    <div class="space-y-2">
                                        <div class="flex justify-between text-sm">
                                            <span>Delivered:</span>
                                            <span class="font-medium">{successful_sms}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span>Failed:</span>
                                            <span class="font-medium">{failed_sms}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span>Other:</span>
                                            <span class="font-medium">{sms_count - successful_sms - failed_sms}</span>
                                        </div>
                                    </div>
                                    
                                    <div class="mt-3">
                                        <a href="{reverse('admin:common_sms_changelist')}" 
                                           class="text-green-500 hover:text-green-700 text-sm flex items-center">
                                            View all SMS
                                            <span class="material-symbols-outlined ml-1 text-base">chevron_right</span>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """,
                    "column": 1,
                    "order": 3,
                },
                
                # Payments & Subscriptions Widget
                {
                    "title": _("Finance"),
                    "content": f"""
                        <div class="p-4">
                            <div class="grid grid-cols-2 gap-6">
                                <div class="border-r pr-5">
                                    <div class="flex justify-between items-baseline">
                                        <div>
                                            <div class="text-2xl font-bold">{payment_count}</div>
                                            <div class="text-sm text-gray-500">Total Payments</div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-lg font-semibold text-green-600">${total_revenue/100:.2f}</div>
                                            <div class="text-xs text-gray-500">Total Revenue</div>
                                        </div>
                                    </div>
                                    
                                    <div class="mt-3 space-y-1">
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                                                Succeeded
                                            </span>
                                            <span class="font-medium">{payment_stats['succeeded']}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-yellow-500 mr-1"></span>
                                                Pending
                                            </span>
                                            <span class="font-medium">{payment_stats['pending']}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-red-500 mr-1"></span>
                                                Failed
                                            </span>
                                            <span class="font-medium">{payment_stats['failed']}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-purple-500 mr-1"></span>
                                                Refunded
                                            </span>
                                            <span class="font-medium">{payment_stats['refunded']}</span>
                                        </div>
                                    </div>
                                    
                                    <div class="mt-3">
                                        <a href="{reverse('admin:common_payment_changelist')}" 
                                           class="text-blue-500 hover:text-blue-700 text-sm flex items-center">
                                            View all payments
                                            <span class="material-symbols-outlined ml-1 text-base">chevron_right</span>
                                        </a>
                                    </div>
                                </div>
                                
                                <div class="">
                                    <div class="flex justify-between items-baseline">
                                        <div>
                                            <div class="text-2xl font-bold">{subscription_count}</div>
                                            <div class="text-sm text-gray-500">Subscriptions</div>
                                        </div>
                                        <div class="text-right">
                                            <div class="text-lg font-semibold text-green-600">{subscription_stats['active']}</div>
                                            <div class="text-xs text-gray-500">Active</div>
                                        </div>
                                    </div>
                                    
                                    <div class="mt-3 space-y-1">
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                                                Active
                                            </span>
                                            <span class="font-medium">{subscription_stats['active']}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-blue-500 mr-1"></span>
                                                Trialing
                                            </span>
                                            <span class="font-medium">{subscription_stats['trialing']}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-orange-500 mr-1"></span>
                                                Past Due
                                            </span>
                                            <span class="font-medium">{subscription_stats['past_due']}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span class="flex items-center">
                                                <span class="w-2 h-2 rounded-full bg-red-500 mr-1"></span>
                                                Canceled
                                            </span>
                                            <span class="font-medium">{subscription_stats['canceled']}</span>
                                        </div>
                                    </div>
                                    
                                    <div class="mt-3">
                                        <a href="{reverse('admin:common_subscription_changelist')}" 
                                           class="text-blue-500 hover:text-blue-700 text-sm flex items-center">
                                            View all subscriptions
                                            <span class="material-symbols-outlined ml-1 text-base">chevron_right</span>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """,
                    "column": 2,
                    "order": 0,
                },
                
                # Activity feed and admin guide
                {
                    "title": _("Recent Activity"),
                    "template": "admin/dashboard/recent_activity.html",
                    "column": 2,
                    "order": 1,
                },
                
                {
                    "title": _("Admin Navigation Guide"),
                    "content": f"""
                        <div class="p-4">
                            <div class="mb-4">
                                <h3 class="text-lg font-semibold mb-2">Main Navigation</h3>
                                <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                                    {" ".join([f'<a href="{reverse(f"admin:common_{model.lower()}_changelist")}" class="bg-gray-100 dark:bg-gray-800 p-2 text-center rounded hover:bg-blue-100 dark:hover:bg-blue-900 transition">{model}</a>' for model in MAIN_NAV_MODELS])}
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <h3 class="text-lg font-semibold mb-2">Categories</h3>
                                <div class="space-y-3">
                                    {" ".join([f'''
                                    <div>
                                        <h4 class="font-medium text-gray-700 dark:text-gray-300 mb-1">{category}</h4>
                                        <div class="grid grid-cols-2 md:grid-cols-3 gap-1 text-sm">
                                            {" ".join([f'<a href="{reverse(f"admin:common_{model.lower()}_changelist")}" class="text-blue-600 dark:text-blue-400 hover:underline">{model}</a>' for model in models])}
                                        </div>
                                    </div>''' for category, models in ADMIN_CATEGORIES.items()])}
                                </div>
                            </div>
                            
                            <div class="mt-4 text-sm text-gray-600 dark:text-gray-400 border-t pt-3">
                                <p>Use the search feature to quickly find specific models or records. The sidebar navigation provides quick access to all models organized by category.</p>
                            </div>
                        </div>
                    """,
                    "column": 2,
                    "order": 2,
                },
            ],
        }
    ]
    
    # Add widgets to context
    context["widgets"] = widgets
    
    return context


def filter_admin_app_list(app_list, request):
    """
    Organize the admin app list into categories based on ADMIN_CATEGORIES.
    
    Args:
        app_list: The list of apps to filter
        request: The current request object
        
    Returns:
        Organized app list
    """
    # For direct model access (e.g., change/add pages), return unmodified
    if getattr(request, 'current_app', None) or not hasattr(request, 'path'):
        return app_list
    
    # Only run this for the main admin index page
    if '/admin/' != request.path and not request.path.endswith('/admin'):
        return app_list
    
    # For superusers, we still show the categories but include all models
    # so we don't filter anything out
    
    # We'll use the navigation defined in UNFOLD settings instead of 
    # manipulating the app_list directly
    
    return app_list