from django.shortcuts import render
from .models import Subscribe
from .forms import NewsletterForm, SubscribeForm
import sendmail
from markdown import markdown
from django.http import HttpResponseRedirect

def newsletter(request):
	if request.user.is_authenticated():
		form=NewsletterForm(request.POST, request.FILES)

		if "newsletter" in request.POST :
	                destination=Subscribe.objects.filter(newsletter=request.POST.get("newsletter"))
		else :
	                destination=Subscribe.objects.only("email") #values("email")
			
		addresses=[]
		for i in destination:
			addresses.append(str(i))
                context={'form':form, 'newsletters':Subscribe.objects.values('newsletter').distinct()}

		if "envoyer" in request.POST:
			email=form.save(commit=False,)
			email.save()

			try:
				sendmail.sendmail(addresses,str(email.subject),markdown(str(email.body)), str(email.attachement.path))
			except:
				sendmail.sendmail(addresses,str(email.subject),markdown(str(email.body)))


		return render(request,'newsletter.html',context)

	else: 
		return HttpResponseRedirect('/')
	
def subscribe_specific(request):
	form = SubscribeForm(request.POST or None )

	if form.is_valid():
		if 'subscribe' in form.POST:
			new_subscribe=form.save(commit=False)
			ip=get_ip(request)
			new_subscribe.save()
		if 'unsubscribe' in form.POST:
			pass

	return render(request, "subscribed.html", context)

def subscribe_default(request):
	try:
		form = SubscribeForm(request.POST or None )
		context={ "subscribe" : True }
		if 'subscribe' in request.POST:
			if form.is_valid():
				new_subscribe=form.save(commit=False)
				ip=get_ip(request)
				new_subscribe.save()
				context={ "subscribe" : True }
			else:
				subscriber=Subscribe.objects.filter(email=request.POST.get("email"))[0]
				if subscriber:
					subscriber.newsletter="default"
					subscriber.save()
					context={"subscribe": True}
				


		elif 'unsubscribe' in request.POST:
			subscriber=Subscribe.objects.filter(email=request.POST.get("email"))[0]
			print subscriber
			subscriber.newsletter="deleted"
			subscriber.save()
			context={ "unsubscribe" : True }

		return render(request, "subscribed.html", context)
	except:
		return HttpResponseRedirect('/')

def get_ip(request):
        try:
                x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forward:
                        ip=x_forward.split(",")[0]
                else:   
                        ip=request.META.get("REMOTE_ADDR")
        except: 
                ip=""

        return ip



