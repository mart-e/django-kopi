from django.db import models

class HttpBLLog(models.Model):
   ip = models.IPAddressField()
   datetime = models.DateTimeField(auto_now_add=True)
   user_agent = models.CharField(max_length=100)
   httpbl = models.IPAddressField()
	
   class Admin:
      list_display = ('ip', 'datetime', 'user_agent', 'httpbl')
