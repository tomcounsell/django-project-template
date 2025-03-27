from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from apps.common.models import User, Team, TeamMember, BlogPost, TodoItem


@admin.register(User)
class UserAdmin(ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ('username', 'email', 'full_name', 'is_staff', 'status_badge')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Active</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-red-500 text-white">Inactive</span>'
        )
    
    status_badge.short_description = "Status"
    full_name.short_description = "Name"


class TeamMemberInline(TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Team)
class TeamAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'member_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TeamMemberInline]
    
    def member_count(self, obj):
        """Return the number of members in the team."""
        count = obj.members.count()
        return format_html(
            '<span class="unfold-badge bg-blue-500 text-white">{}</span>',
            count
        )
    
    member_count.short_description = 'Members'


@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ('user', 'team', 'role_badge')
    list_filter = ('role', 'team')
    search_fields = ('user__username', 'user__email', 'team__name')
    autocomplete_fields = ['user', 'team']
    
    def role_badge(self, obj):
        colors = {
            'owner': 'bg-purple-500',
            'admin': 'bg-red-500',
            'member': 'bg-blue-500',
            'guest': 'bg-gray-500'
        }
        color = colors.get(obj.role, 'bg-gray-500')
        
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            color, obj.get_role_display()
        )
    
    role_badge.short_description = 'Role'


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ('title', 'author_display', 'location_display', 'publishing_status', 'expiration_status')
    list_filter = ('published_at', 'expired_at')
    search_fields = ('title', 'subtitle', 'content', 'tags')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'modified_at', 'authored_at')
    
    fieldsets = (
        ("Content", {
            "fields": ("title", "subtitle", "content", "featured_image", "reading_time_minutes", "tags")
        }),
        ("Author Information", {
            "fields": ("author", "is_author_anonymous", "authored_at")
        }),
        ("Publication Status", {
            "fields": ("published_at", "edited_at", "unpublished_at")
        }),
        ("Expiration", {
            "fields": ("valid_at", "expired_at")
        }),
        ("Location", {
            "fields": ("address", "latitude", "longitude")
        }),
        ("Permalink", {
            "fields": ("slug",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "modified_at")
        }),
    )
    
    def author_display(self, obj):
        return obj.author_display_name
    
    def location_display(self, obj):
        if obj.address:
            return format_html(
                '<span class="unfold-badge bg-blue-500 text-white">{}</span>',
                str(obj.address)[:30]
            )
        return "-"
        
    def publishing_status(self, obj):
        if obj.is_published:
            return format_html(
                '<span class="unfold-badge bg-green-500 text-white">Published</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-gray-500 text-white">Draft</span>'
        )
    
    def expiration_status(self, obj):
        if obj.is_expired:
            return format_html(
                '<span class="unfold-badge bg-red-500 text-white">Expired</span>'
            )
        return format_html(
            '<span class="unfold-badge bg-green-500 text-white">Active</span>'
        )
    
    author_display.short_description = "Author"
    location_display.short_description = "Location"
    publishing_status.short_description = "Status"
    expiration_status.short_description = "Expiration"


@admin.register(TodoItem)
class TodoItemAdmin(ModelAdmin):
    list_display = ('title', 'priority_badge', 'category_badge', 'status_badge', 'assignee_display', 'due_date_display')
    list_filter = ('priority', 'category', 'status', 'assignee')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'modified_at', 'completed_at')
    
    fieldsets = (
        ("Task Information", {
            "fields": ("title", "description", "priority", "category", "status")
        }),
        ("Assignment", {
            "fields": ("assignee", "due_at")
        }),
        ("Completion", {
            "fields": ("completed_at",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "modified_at")
        }),
    )
    
    def priority_badge(self, obj):
        colors = {
            'HIGH': 'bg-red-500',
            'MEDIUM': 'bg-yellow-500',
            'LOW': 'bg-blue-500'
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            colors.get(obj.priority, 'bg-gray-500'),
            obj.get_priority_display()
        )
    
    def category_badge(self, obj):
        colors = {
            'FRONTEND': 'bg-purple-500',
            'BACKEND': 'bg-blue-500',
            'API': 'bg-green-500',
            'DATABASE': 'bg-yellow-500',
            'PERFORMANCE': 'bg-orange-500',
            'SECURITY': 'bg-red-500',
            'DOCUMENTATION': 'bg-gray-500',
            'TESTING': 'bg-teal-500',
            'GENERAL': 'bg-gray-500',
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            colors.get(obj.category, 'bg-gray-500'),
            obj.get_category_display()
        )
    
    def status_badge(self, obj):
        colors = {
            'TODO': 'bg-blue-500',
            'IN_PROGRESS': 'bg-yellow-500',
            'BLOCKED': 'bg-red-500',
            'DONE': 'bg-green-500'
        }
        return format_html(
            '<span class="unfold-badge {} text-white">{}</span>',
            colors.get(obj.status, 'bg-gray-500'),
            obj.get_status_display()
        )
    
    def assignee_display(self, obj):
        if obj.assignee:
            return f"{obj.assignee.first_name} {obj.assignee.last_name}"
        return "-"
    
    def due_date_display(self, obj):
        if not obj.due_at:
            return "-"
        
        if obj.is_overdue:
            return format_html(
                '<span class="unfold-badge bg-red-500 text-white">{}</span>',
                obj.time_remaining_display
            )
        return format_html(
            '<span class="unfold-badge bg-blue-500 text-white">{}</span>',
            obj.time_remaining_display
        )
    
    priority_badge.short_description = "Priority"
    category_badge.short_description = "Category" 
    status_badge.short_description = "Status"
    assignee_display.short_description = "Assignee"
    due_date_display.short_description = "Due Date"
