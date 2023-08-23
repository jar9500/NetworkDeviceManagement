from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponse
from .models import Device, Log
import paramiko
import time
from datetime import datetime
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    all_devices = Device.objects.all()
    cisco_device = Device.objects.filter(vendor='cisco')
    mikrotik_device = Device.objects.filter(vendor='mikrotik')
    recent_event = Log.objects.all().order_by("-id")[:5]

    context = {
        'total_devices': len(all_devices),
        'cisco_device': len(cisco_device),
        'mikrotik_device': len(mikrotik_device),
        'recent_event': recent_event
    }
    return render(request, 'home.html', context)

@login_required
def devices(request):
    all_devices = Device.objects.all()

    context = {
        'all_devices': all_devices,
        'total_devices' : len(all_devices)
    }

    return render(request, 'devices.html', context)

@login_required
def configuration(request):
    if request.method == 'POST':
        selected_device_id = request.POST.getlist('device')
        mikrotik_cmd = request.POST['mikrotik_cmd'].splitlines()
        cisco_cmd = request.POST['cisco_cmd'].splitlines()
        for x in selected_device_id:
            dev = get_object_or_404(Device, pk=x)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=dev.IP_address, username=dev.username, password=dev.password, port=dev.SSH_port)
            try:    
                if dev.vendor.lower() == 'mikrotik':
                    for cmd in mikrotik_cmd:
                        stdin, stdout, stderr = ssh_client.exec_command(cmd)
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send("conf terminal\n")
                    for cmd in cisco_cmd:
                        conn.send(cmd+"\n")
                        time.sleep(1)
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) ", action="Configuration", status="Success", time=datetime.now(), message="Complete - No Error ")
                log.save()
            except Exception as Exc:
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) ", action="Configuration", status="Error", time=datetime.now(), message=Exc)
                log.save()
        return redirect('home')

    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
        }
        return render(request, 'configuration.html', context)

@login_required
def verify(request):
    if request.method == 'POST':
        result = []
        selected_device_id = request.POST.getlist('device')
        mikrotik_verify_select = request.POST['mikrotik_verify_select'].splitlines()
        mikrotik_verify_cmd = request.POST['mikrotik_verify_cmd'].splitlines()
        cisco_verify_select = request.POST['cisco_verify_select'].splitlines()
        cisco_verify_cmd = request.POST['cisco_verify_cmd'].splitlines()
        for x in selected_device_id:
            dev = get_object_or_404(Device, pk=x)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=dev.IP_address, username=dev.username, password=dev.password, port=dev.SSH_port)
            try:
                if dev.vendor.lower() == 'mikrotik':
                    for mikrotikselect in mikrotik_verify_select:
                        stdin, stdout, stderr = ssh_client.exec_command(mikrotikselect)
                        result.append("Result on {}".format(dev.IP_address))
                        result.append(stdout.read().decode())
                    for mikrotikcmd in mikrotik_verify_cmd:
                        stdin, stdout, stderr = ssh_client.exec_command(mikrotikcmd)
                        result.append("Result on {}".format(dev.IP_address))
                        result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send("terminal length 0\n")
                    for ciscoselect in cisco_verify_select:
                        result.append("Result on {}".format(dev.IP_address))
                        conn.send(ciscoselect+"\n")
                        time.sleep(5)
                        output = conn.recv(65535)
                        result.append (output.decode())
                    for ciscocmd in cisco_verify_cmd:
                        result.append("Result on {}".format(dev.IP_address))
                        conn.send(ciscocmd+"\n")
                        time.sleep(5)
                        output = conn.recv(65535)
                        result.append (output.decode())
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) ", action="Verify", status="Success", time=datetime.now(), message="Complete - No Error")
                log.save()
            except Exception as Exc:
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) " , action="Verify", status="Error", time=datetime.now(), message=Exc)
                log.save()
        result = "\n".join(result)
        return render(request,'verifyResult.html',{"result":result})
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
        }
        return render(request, 'verify.html', context)


@login_required
def log(request):
    logs = Log.objects.all()
    context = {
            'logs': logs
        }
    return render(request, 'log.html', context)

@login_required
def saveconfig(request):
    timenow = datetime.today().strftime("%d-%m-%Y,%H:%M:%S")
    if request.method == 'POST':
        result = []
        selected_device_id = request.POST.getlist('device')
        for x in selected_device_id:
            dev = get_object_or_404(Device, pk=x)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=dev.IP_address, username=dev.username, password=dev.password, port=dev.SSH_port)
            try:
                if dev.vendor.lower() == 'mikrotik':
                    stdin, stdout, stderr = ssh_client.exec_command("export file= Backup-" + timenow)
                    stdin, stdout, stderr = ssh_client.exec_command("file print")
                    result.append("Result on {}".format(dev.IP_address))
                    result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send("terminal length 0\n")
                    result.append("Result on {}".format(dev.IP_address))
                    conn.send("copy running-config startup-config \n\n\n")
                    time.sleep(5)
                    output = conn.recv(65535)
                    result.append (output.decode())
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) ", action="Save Config", status="Success", time=datetime.now(), message="Complete - No Error")
                log.save()
            except Exception as Exc:
                log = Log(target=dev.IP_address + " ( " +dev.hostname+" ) " , action="Save Config", status="Error", time=datetime.now(), message=Exc)
                log.save()
        result = "\n".join(result)
        return render(request,'verifyResult.html',{"result":result})
    
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
        }
        return render(request, 'saveconfig.html', context)