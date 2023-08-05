"""
-------------------------------------------------------------------------
	Author: Dadaso Zanzane

	git clone https://github.com/dadasoz-cuelogic/blog-app.git 
--------------------------------------------------------------------------

"""
from django.db import models
from django_cuelogic_comments.models import Comments
from django import forms

class CommentsForm(forms.ModelForm):
	
	def __init__(self,*args,**kwargs):
		super(CommentsForm,self).__init__(*args,**kwargs)
		if(len(args)>0):
			post_id=args[1]
			self.fields["post_id"]=forms.IntegerField(widget=forms.HiddenInput(attrs={"value":post_id}),required=False)

	class Meta:
		model = Comments
		exclude = ('updated', 'created')   
		fields = ('name','email','contents','post_id')

	name = forms.CharField(label='Name', max_length=50, required=False)
	email = forms.CharField(label='Email', max_length=50, required=False)
	contents = forms.CharField(label='Comment',widget=forms.Textarea(attrs={'rows': 5, 'cols': 50}),required=False)
	post_id = forms.IntegerField()
