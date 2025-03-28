"""
Views for team management including listing, creation, editing, and deletion.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from apps.common.models.team import Role, Team, TeamMember
from apps.public.views.helpers.main_content_view import MainContentView


class TeamListView(LoginRequiredMixin, MainContentView, ListView):
    """View for listing teams that the user belongs to."""
    
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        """Return only teams that the user is a member of."""
        return self.request.user.teams.all().order_by('name')
    
    def get_context_data(self, **kwargs):
        """Add additional context data for team list."""
        context = super().get_context_data(**kwargs)
        
        # Group teams by the user's role
        user = self.request.user
        context.update({
            'owned_teams': Team.objects.filter(
                teammember__user=user, 
                teammember__role=Role.OWNER.value
            ),
            'admin_teams': Team.objects.filter(
                teammember__user=user, 
                teammember__role=Role.ADMIN.value
            ),
            'member_teams': Team.objects.filter(
                teammember__user=user, 
                teammember__role=Role.MEMBER.value
            ),
        })
        return context


class TeamCreateView(LoginRequiredMixin, MainContentView, CreateView):
    """View for creating a new team."""
    
    model = Team
    template_name = 'teams/team_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('public:team-list')
    
    def get_context_data(self, **kwargs):
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Team'
        context['submit_text'] = 'Create Team'
        return context
    
    def form_valid(self, form):
        """Process valid form data and add the creator as team owner."""
        with transaction.atomic():
            # Auto-generate slug from name
            name = form.cleaned_data['name']
            form.instance.slug = slugify(name)
            form.instance.is_active = True
            
            # Save the team
            response = super().form_valid(form)
            
            # Add the current user as an owner of the team
            TeamMember.objects.create(
                team=self.object,
                user=self.request.user,
                role=Role.OWNER.value
            )
            
            messages.success(
                self.request, 
                f'Team "{self.object.name}" created successfully!'
            )
            
            return response


class TeamDetailView(LoginRequiredMixin, MainContentView, DetailView):
    """View for team details and member management."""
    
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'
    slug_url_kwarg = 'team_slug'
    
    def get_queryset(self):
        """Return only teams that the user is a member of."""
        return self.request.user.teams.all()
    
    def get_context_data(self, **kwargs):
        """Add team members to context."""
        context = super().get_context_data(**kwargs)
        context['members'] = TeamMember.objects.filter(
            team=self.object
        ).select_related('user').order_by('role', 'user__first_name')
        
        # Determine if user can manage team
        context['can_manage'] = self.object.user_can_manage(self.request.user)
        context['can_delete'] = self.object.user_can_delete(self.request.user)
        
        # Group members by role
        context['owners'] = context['members'].filter(role=Role.OWNER.value)
        context['admins'] = context['members'].filter(role=Role.ADMIN.value)
        context['regular_members'] = context['members'].filter(role=Role.MEMBER.value)
        
        return context


class TeamUpdateView(LoginRequiredMixin, MainContentView, UpdateView):
    """View for updating team details."""
    
    model = Team
    template_name = 'teams/team_form.html'
    fields = ['name', 'description', 'is_active']
    slug_url_kwarg = 'team_slug'
    
    def get_queryset(self):
        """Return only teams that the user can manage."""
        return Team.objects.filter(
            teammember__user=self.request.user,
            teammember__role__in=[Role.OWNER.value, Role.ADMIN.value]
        )
    
    def get_context_data(self, **kwargs):
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Team: {self.object.name}'
        context['submit_text'] = 'Update Team'
        return context
    
    def get_success_url(self):
        """Return to team detail view after successful update."""
        return reverse('public:team-detail', kwargs={'team_slug': self.object.slug})
    
    def form_valid(self, form):
        """Handle valid form submission."""
        # Update slug if name changed
        if form.cleaned_data['name'] != self.object.name:
            form.instance.slug = slugify(form.cleaned_data['name'])
            
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f'Team "{self.object.name}" updated successfully!'
        )
        return response


class TeamDeleteView(LoginRequiredMixin, MainContentView, DeleteView):
    """View for deleting a team."""
    
    model = Team
    template_name = 'teams/team_confirm_delete.html'
    success_url = reverse_lazy('public:team-list')
    slug_url_kwarg = 'team_slug'
    
    def get_queryset(self):
        """Return only teams that the user can delete (owner)."""
        return Team.objects.filter(
            teammember__user=self.request.user,
            teammember__role=Role.OWNER.value
        )
    
    def delete(self, request, *args, **kwargs):
        """Process team deletion and add success message."""
        team = self.get_object()
        team_name = team.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Team "{team_name}" has been deleted.')
        return response