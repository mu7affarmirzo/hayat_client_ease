from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

from core.models import ReferralDoctorModel


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to superusers only"""
    def test_func(self):
        return self.request.user.is_superuser


class ReferralDoctorListView(LoginRequiredMixin, ListView):
    model = ReferralDoctorModel
    template_name = 'adminstration/doctors/doctor_list.html'
    context_object_name = 'doctors'
    ordering = ['-is_active', 'l_name', 'f_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add filtering options if needed
        return queryset


class ReferralDoctorDetailView(LoginRequiredMixin, DetailView):
    model = ReferralDoctorModel
    template_name = 'adminstration/doctors/doctor_detail.html'
    context_object_name = 'doctor'


class ReferralDoctorCreateView(LoginRequiredMixin, CreateView):
    model = ReferralDoctorModel
    template_name = 'adminstration/doctors/doctor_form.html'
    fields = ['f_name', 'mid_name', 'l_name', 'email', 'gender', 'rate', 'is_active']
    success_url = reverse_lazy('administration:doctor_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Доктор-реферал успешно добавлен.')
        return super().form_valid(form)


class ReferralDoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = ReferralDoctorModel
    template_name = 'adminstration/doctors/doctor_form.html'
    fields = ['f_name', 'mid_name', 'l_name', 'email', 'gender', 'rate', 'is_active']
    context_object_name = 'doctor'

    def get_success_url(self):
        return reverse_lazy('administration:doctor_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        messages.success(self.request, 'Информация о докторе-реферале успешно обновлена.')
        return super().form_valid(form)


class ReferralDoctorDeleteView(LoginRequiredMixin, DeleteView):
    model = ReferralDoctorModel
    template_name = 'adminstration/doctors/doctor_confirm_delete.html'
    context_object_name = 'doctor'
    success_url = reverse_lazy('administration:doctor_list')

    def delete(self, request, *args, **kwargs):
        # Could also consider just setting is_active=False instead of deleting
        messages.success(request, 'Доктор-реферал успешно удален.')
        return super().delete(request, *args, **kwargs)