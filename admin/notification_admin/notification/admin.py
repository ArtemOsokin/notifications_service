# type: ignore

from django.contrib import admin

from .models import MailingTask, Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('template_type', 'title', 'subject', 'channel',)
    fields = (
        'title', 'subject', 'from_email', 'html_template', 'plain_text',
        'is_html', 'is_text', 'template_type', 'channel'
    )
    list_per_page = 20
    sortable_by = ('title', 'template_type', 'creation_date',)
    search_fields = ('title', 'subject', 'template_type', 'channel')
    save_as = True


@admin.register(MailingTask)
class MailingTaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'status', 'is_promo', 'priority', 'scheduled_datetime', 'execution_datetime'
    )
    fields = (
        'title', 'type_mailing', 'is_promo', 'priority', 'template', 'context',
        'scheduled_datetime',
    )
    list_per_page = 20
    search_fields = ('context',)
    save_as = True
