from django.shortcuts import render
from .models import Subscribe
from .forms import NewsletterForm
import sendmail
from markdown import markdown

def newsletter(request):
	if request.user.is_authenticated():
		form=NewsletterForm(request.POST, request.FILES)
		destination=Subscribe.objects.only("email")
		a=[]
		for i in destination:
			a.append(str(i))
		context={'form':form}	

		if form.is_valid():
			email=form.save(commit=False)
			file0=str(email.attachement)
			email.save()
			file0=str(email.attachement)
			sendmail.sendmail(a,str(email.subject),markdown(str(email.body)), str(email.attachement.path))

		return render(request,'newsletter.html',context)

	else: 
		return HttpResponseRedirect('/')
	


