from django.shortcuts import render
from django.shortcuts import get_object_or_404, render_to_response 
from django.http import HttpResponseRedirect, HttpResponse 
from django.template import RequestContext
from django_cuelogic_comments.forms import CommentsForm
from django_cuelogic_comments.models import Comments
from django.template.loader import render_to_string
from django.middleware import csrf
from django.http import HttpResponseRedirect, HttpResponse 


# Create your views here.
def get(request,parent,delete=False,reply=False,user="Anonymous"): 
	print delete
	form = CommentsForm(request.POST,parent) # get request
	data={}
	latest_comments = Comments.objects.filter(post_id=parent).order_by('-pub_date')
	if request.method == 'POST':
		if("reply_msg" in request.POST):
			reply_msg=request.POST["reply_msg"]
			post_id=request.POST["post_id"]
			parent_id=request.POST["parent_id"]
			name=request.POST["user"]
			comment_data=Comments(name=name,contents=reply_msg,post_id=post_id, parent=parent_id)
			comment_data.save()
		elif("action" in request.POST):
			if(request.POST["action"]=="delete"):
				try:
					delete = Comments.objects.get(pk=request.POST["id"]).delete()
				except:
					pass
		else:
			form.save()
		form = CommentsForm(request.GET,parent)
	data.update({"form":form,"post_id":parent,"user":user,"csrf_token":get_or_create_csrf_token(request),"latest_comments":latest_comments,"delete":delete,"reply":reply}) # Update the global data dictionary
	return render_to_string('comments/index.html',  data) # render the template with data and request object

def get_or_create_csrf_token(request):
    token = request.META.get('CSRF_COOKIE', None)
    if token is None:
        token = csrf._get_new_csrf_key()
        request.META['CSRF_COOKIE'] = token
    request.META['CSRF_COOKIE_USED'] = True
    return token