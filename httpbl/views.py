from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect
from httpbl.models import HttpBLLog
import socket

class HttpBLMiddleware(object):
   """
   "HttpBL" Middleware by iamtgc@gmail.com 
   """
   def __init__(self, age=None, threat=None, classification=None):
      if age is None:
         self.age = getattr(settings, 'HTTPBLAGE', 14)
      else:
         self.age = age
      if threat is None:
         self.threat = getattr(settings, 'HTTPBLTHREAT', 30)
      else:
         self.threat = threat
      if classification is None:
         self.classification = getattr(settings, 'HTTPBLCLASS', 7)
      else:
         self.classification = classification

   def process_request(self, request, detail=False):
      """Check if the visitor is blacklisted

      request : a django request object
      detail : if True, will return a dictonnary with the detail of the threat
         if the visitor is blacklisted, None otherwise
               if False, will return a HttpResponse if blacklisted, None otherwise"""
      self.ip = request.META.get('REMOTE_ADDR')
      self.detail = detail
      return self.check_ip()


   def check_ip(self):
      if settings.HTTPBLKEY:
         
         self.iplist = self.ip.split('.')
         self.iplist.reverse()

         self.domain = 'dnsbl.httpbl.org'

         self.query = settings.HTTPBLKEY + "." + ".".join(self.iplist) + "." + self.domain

         try:
            self.result = socket.gethostbyname(self.query)
         except socket.gaierror:
            return None

         self.resultlist = self.result.split('.')

         if (int(self.resultlist[1]) <= self.age and 
             int(self.resultlist[2]) >= self.threat and 
             int(self.resultlist[3]) & self.classification > 0):

            self.log = HttpBLLog (ip = self.ip,
                                  user_agent = request.META.get('HTTP_USER_AGENT'),
                                  httpbl = self.result)
            self.log.save()

            if not self.detail:
               if settings.HTTPBLREDIRECT:
                  return HttpResponsePermanentRedirect(settings.HTTPBLREDIRECT)
               else:
                  return HttpResponseNotFound('<h1>Not Found</h1>')
            else:
               return {'age':self.resultlist[1], 'threat':self.resultlist[2], 'classification':self.resultlist[3]}
      
      return None

