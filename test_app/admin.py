from django.contrib import admin
from test_app.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(SalesData)
admin.site.register(UploadedFile)