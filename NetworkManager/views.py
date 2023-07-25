from django.shortcuts import render, HttpResponse
from .models import Device

def home(request):
    all_devices = Device.objects.all()
    cisco_device = Device.objects.filter(vendor='cisco')
    mikrotik_device = Device.objects.filter(vendor='mikrotik')
    
    context = {
        'all_devices': len(all_devices),
        'cisco_device': len(cisco_device),
        'mikrotik_device': len(mikrotik_device),
    }
    return render(request, 'home.html', context)
