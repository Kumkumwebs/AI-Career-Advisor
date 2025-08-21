from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recommend/', views.recommend, name='recommend'),
    path('upload_resume/', views.upload_resume, name='upload_resume'),
    path('enter_skills/', views.enter_skills, name='enter_skills'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('upload/', views.upload_or_enter, name='upload'),
    path('submit-resume/', views.submit_resume, name='submit_resume'),


]
