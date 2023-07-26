from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import Device
import paramiko
import time

def home(request):
    all_devices = Device.objects.all()
    cisco_device = Device.objects.filter(vendor='cisco')
    mikrotik_device = Device.objects.filter(vendor='mikrotik')
    
    context = {
        'total_devices': len(all_devices),
        'cisco_device': len(cisco_device),
        'mikrotik_device': len(mikrotik_device),
    }
    return render(request, 'home.html', context)

def devices(request):
    all_devices = Device.objects.all()

    context = {
        'all_devices': all_devices,
        'total_devices' : len(all_devices)
    }

    return render(request, 'devices.html', context)

def configuration(request):
    if request.method == 'POST':
        selected_device_id = request.POST.get('device')
        mikrotik_cmd = request.POST['mikrotik_cmd'].splitlines()
        cisco_cmd = request.POST['cisco_cmd'].splitlines()
        for x in selected_device_id:
            dev = get_object_or_404(Device, pk=x)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=dev.IP_address, username=dev.username, password=dev.password)

            if dev.vendor.lower() == 'mikrotik':
                for cmd in mikrotik_cmd:
                    ssh_client.exec_command(cmd)
            else:
                conn = ssh_client.invoke_shell()
                conn.send("conf terminal\n")
                for cmd in cisco_cmd:
                    conn.send(cmd+"\n")
                    time.sleep(1)
        return redirect('home')
    
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Configure'
        }
    
    return render(request, 'configuration.html', context)
