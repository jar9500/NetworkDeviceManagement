from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponse
from .models import Device, Log
import paramiko
import time
from datetime import datetime

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
        selected_device_id = request.POST.getlist('devices')
        mikrotik_cmd = request.POST['mikrotik_cmd'].splitlines()
        cisco_cmd = request.POST['cisco_cmd'].splitlines()
        for x in selected_device_id:
            try:
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
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) ", action="Configuration", status="Success", time=datetime.now(), message="Complete - No Error")
                log.save()
            except Exception as Exc:
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) ", action="Configuration", status="Error", time=datetime.now(), message=Exc)
                log.save()
        return redirect('home')

    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Terminal'
        }
        return render(request, 'configuration.html', context)

def verify(request):
    if request.method == 'POST':
        result = []
        selected_device_id = request.POST.getlist('device')
        mikrotik_cmd = request.POST['mikrotik_cmd'].splitlines()
        cisco_cmd = request.POST['cisco_cmd'].splitlines()
        for x in selected_device_id:
            dev = get_object_or_404(Device, pk=x)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=dev.IP_address, username=dev.username, password=dev.password)
            try:
                if dev.vendor.lower() == 'mikrotik':
                    for cmd in mikrotik_cmd:
                        stdin, stdout, stderr = ssh_client.exec_command(cmd)
                        result.append("Result on {}".format(dev.IP_address))
                        result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send("terminal length 0\n")
                    for cmd in cisco_cmd:
                        result.append("Result on {}".format(dev.IP_address))
                        conn.send(cmd+"\n")
                        time.sleep(1)
                        output = conn.recv(65535)
                        result.append (output.decode())
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) ", action="Verify", status="Success", time=datetime.now(), message="Complete - No Error")
                log.save()
            except Exception as Exc:
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) " , action="Verify", status="Error", time=datetime.now(), message=Exc)
                log.save()

        result = "\n".join(result)
        return render(request,'verify.html',{"result":result})
    
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Verify Configuration',
            'mikrotik_verify': 'export',
            'cisco_verify': 'show running-config',
        }
    
    return render(request, 'configuration.html', context)

def log(request):
    logs = Log.objects.all()

    context = {
            'logs': logs
        }
    
    return render(request, 'log.html', context)
