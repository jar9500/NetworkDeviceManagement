from django.db import models

class Device(models.Model):
    IP_address = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, blank=True)
    SSH_port = models.IntegerField(default=22)

    CHOOSE_VENDOR= (
        ('mikrotik', 'Mikrotik'),
        ('cisco', 'Cisco')
    )
    vendor = models.CharField(max_length=255, choices= CHOOSE_VENDOR, blank=True)

    TYPE_CHOICES = (
        ('router', 'Router'),
        ('switch', 'Switch')
    )
    device_type = models.CharField(max_length=255, choices=TYPE_CHOICES, blank=True)

    def __str__(self):
        return "{} - {}".format(self.hostname, self.IP_address)
    
class Log(models.Model):
    target = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    time = models.DateTimeField(null=True)
    message = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{} -  {} - {}".format(self.target, self.action, self.status)