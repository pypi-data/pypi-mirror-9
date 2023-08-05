from django.contrib import admin

# Register your models here.

from .models import Subscribe


class SubscribeAdmin(admin.ModelAdmin):
	list_display= ['email', 'timestamp','ip_address']
	class Meta:
		model = Subscribe

admin.site.register(Subscribe,SubscribeAdmin)

