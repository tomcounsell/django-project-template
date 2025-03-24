from django.contrib import admin
from apps.common.models import User, Team, TeamMember


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'member_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TeamMemberInline]
    
    def member_count(self, obj):
        """Return the number of members in the team."""
        return obj.members.count()
    
    member_count.short_description = 'Members'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role')
    list_filter = ('role', 'team')
    search_fields = ('user__username', 'user__email', 'team__name')
    autocomplete_fields = ['user', 'team']
