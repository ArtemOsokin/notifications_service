from django.contrib import admin
from .models import Template, MailingTask


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('template_key', 'title', 'subject', 'adapter',)
    fields = (
        'title', 'subject', 'from_email', 'html_template', 'plain_text',
        'is_html', 'is_text', 'template_key', 'adapter'
    )
    list_per_page = 20
    sortable_by = ('title', 'template_key', 'creation_date',)
    search_fields = ('title', 'subject', 'template_key', 'adapter')
    save_as = True


@admin.register(MailingTask)
class MailingTaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'status', 'is_promo', 'priority', 'scheduled_datetime', 'repeat_frequency', 'execution_datetime'
    )
    fields = (
        'title', 'type_mailing', 'is_promo', 'priority', 'template', 'context',
        'scheduled_datetime', 'repeat_frequency',
    )
    list_per_page = 20
    search_fields = ('context',)
    save_as = True
