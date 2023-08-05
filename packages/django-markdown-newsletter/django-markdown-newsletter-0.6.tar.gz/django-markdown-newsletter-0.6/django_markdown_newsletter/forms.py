from django import forms
from .models import Subscribe, Newsletter
from pagedown.widgets import PagedownWidget

class SubscribeForm(forms.ModelForm):
	class Meta:
        	model = Subscribe
		fields= ["email",]
	        widgets = {
	            'email' : forms.TextInput(attrs = {'placeholder': 'Adresse E-mail', 'type' : 'email' , 'id' : 'email'}),
        	    }

class NewsletterForm(forms.ModelForm):
        body = forms.CharField(widget=PagedownWidget())
	newsletter=forms.ChoiceField(widget=forms.Select(), 
        choices = ([(x["newsletter"],x["newsletter"]) for x in Subscribe.objects.values('newsletter').distinct()]) , initial='default')
	class Meta:
		model = Newsletter
		exclude=[]

	        
