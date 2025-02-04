from django.shortcuts import redirect, render


# @role_required(role='logus', login_url='logus_auth:logout')
def register_booking_view(request):

    # if request.method == 'POST':
    #     form = BookingForm(request.POST)
    #     if form.is_valid():
    #         booking = form.save()
    #
    #         illness_history = booking.illness_history.first()
    #         is_sick_leave = form.cleaned_data.get('is_sick_leave', False)
    #         return redirect('logus_booking:check-in-update', pk=booking.pk)
    #         # return redirect('logus_auth:main_screen')
    # else:
    #     form = BookingForm()
    # patients = PatientModel.objects.all()
    # rooms = AvailableRoomModel.objects.all()
    # room_types = AvailableRoomsTypeModel.objects.all()
    # tariffs = AvailableTariffModel.objects.all()
    return render(
        request, 'reception/create_booking.html',
        {

        }
    )