from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

from core.models import TherapistModel, ReferralDoctorModel


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to superusers only"""
    def test_func(self):
        return self.request.user.is_superuser


class TherapistListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    model = TherapistModel
    template_name = 'adminstration/therapists/therapist_list.html'
    context_object_name = 'therapists'
    ordering = ['l_name', 'f_name']


class TherapistDetailView(LoginRequiredMixin, SuperuserRequiredMixin, DetailView):
    model = TherapistModel
    template_name = 'adminstration/therapists/therapist_detail.html'
    context_object_name = 'therapist'


class TherapistCreateView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = TherapistModel
    template_name = 'adminstration/therapists/therapist_form.html'
    fields = ['f_name', 'l_name', 'm_name', 'phone_number', 'sex', 'rate']
    success_url = reverse_lazy('administration:therapist_list')

    def form_valid(self, form):
        messages.success(self.request, 'Массажист успешно добавлен.')
        return super().form_valid(form)


class TherapistUpdateView(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    model = TherapistModel
    template_name = 'adminstration/therapists/therapist_form.html'
    fields = ['f_name', 'l_name', 'm_name', 'phone_number', 'sex', 'rate']
    context_object_name = 'therapist'

    def get_success_url(self):
        return reverse_lazy('administration:therapist_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Информация о Массажисте успешно обновлена.')
        return super().form_valid(form)


class TherapistDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, DeleteView):
    model = TherapistModel
    template_name = 'adminstration/therapists/therapist_confirm_delete.html'
    context_object_name = 'therapist'
    success_url = reverse_lazy('administration:therapist_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Массажист успешно удален.')
        return super().delete(request, *args, **kwargs)