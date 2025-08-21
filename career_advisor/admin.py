from django.contrib import admin
from .models import ResumeSubmission
from .models import ContactMessage


admin.site.register(ResumeSubmission)
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('name', 'email', 'subject', 'message')
