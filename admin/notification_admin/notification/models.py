import uuid

from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField


class TimeStampedIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        abstract = True


class TemplateKeys(models.TextChoices):
    """Перечень кодов шаблонов"""

    weekly_personal_mailing_movies = 'weekly_personal_mailing_movies', _('еженедельная персональная подборка фильмов')
    monthly_personal_statistic_views = 'monthly_personal_statistic_views', _('ежемесячная персональная статистика просмотров')
    daily_personal_statistic_likes = 'daily_personal_statistic_likes', _('ежедневная персональная статистика по лайкам рецензий')
    email_confirmation = 'email_confirmation', _('подтверждение адреса электронной почты при регистрации')


class AdapterTypes(models.TextChoices):
    """Типы адаптеров для отправки уведомлений"""
    email = 'email'
    sms = 'sms'
    websocket = 'websocket'


class Template(TimeStampedIDModel):
    """Шаблоны уведомлений"""
    title = models.CharField(_('наименование шаблона уведомления'), max_length=120, blank=False, null=True)
    subject = models.CharField(_('тема уведомления'), max_length=120, blank=True, null=True)
    from_email = models.CharField(_('электронная почта отправителя'), max_length=120, blank=True, null=True)
    html_template = HTMLField(_('содержание html-шаблона'), blank=True, null=True)
    plain_text = models.TextField(_('содержание текстового шаблона'), blank=True, null=True)
    is_html = models.BooleanField(default=False)
    is_text = models.BooleanField(default=False)
    template_key = models.CharField(_('вид шаблона'), choices=TemplateKeys.choices, max_length=50)
    adapter = models.CharField(
        _('используемый адаптер для отправки уведомления'),
        choices=AdapterTypes.choices,
        max_length=50,
        default=AdapterTypes.email,
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()

        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def _get_body(self):
        if self.is_text:
            return self.plain_text

        return self.html_template

    def __str__(self):
        return f'Template <{self.title}> for sending by <{self.adapter}>'

    class Meta:
        db_table = "notification\".\"templates"
        verbose_name = _('шаблон уведомления')
        verbose_name_plural = _('шаблоны уведомлений')
        managed = True


class NotificationType(models.TextChoices):
    to_immediate_send = 'To immediate send', _('для немедленной отправки')
    to_scheduled_send = 'To scheduled send', _('для отправки планировщиком')


class NotificationStatus(models.TextChoices):
    pending = 'Pending', _('ожидает обработки')
    in_processing = 'In processing', _('в процессе обработки')
    completed = 'Completed', _('успешно завершена')
    cancelled = 'Cancelled', _('отменена')


class NotificationPriority(models.TextChoices):
    high = 'high', _('высокий приоритет')
    medium = 'medium', _('средний приоритет')
    low = 'low', _('низкий приоритет')


class RepeatFrequency(models.TextChoices):
    one_time = 'one_time', _('однократно')
    daily = 'daily', _('ежедневно')
    weekly = 'weekly', _('еженедельно')
    monthly = 'monthly', _('ежемесячно')


class MailingTask(TimeStampedIDModel):
    """Рассылка"""
    title = models.CharField(_('наименование рассылки'), max_length=120, blank=False, null=True)
    type_mailing = models.CharField(
        _('вид рассылки'),
        max_length=250,
        choices=NotificationType.choices,
        default=NotificationType.to_scheduled_send,
    )
    status = models.CharField(
        _('статус рассылки'),
        max_length=250,
        choices=NotificationStatus.choices,
        default=NotificationStatus.pending,
    )
    is_promo = models.BooleanField(_('рекламная рассылка'), default=True)
    priority = models.CharField(
        _('приоритет рассылки'),
        max_length=30,
        choices=NotificationPriority.choices,
        default=NotificationPriority.low,
    )
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, verbose_name=_('шаблон уведомления'))
    context = JSONField(_('контекст рассылки'), default=dict())
    scheduled_datetime = models.DateTimeField(_('плановые дата и время рассылки'), blank=True, null=True)
    repeat_frequency = models.CharField(
        _('периодичность рассылки'),
        max_length=20,
        choices=RepeatFrequency.choices,
    )
    execution_datetime = models.DateTimeField(_('фактическое время завершения рассылки'), blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()

        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Mailing <{self.title}>'

    class Meta:
        db_table = "notification\".\"mailing_tasks"
        verbose_name = _('задачу рассылки')
        verbose_name_plural = _('задачи рассылки')
        managed = True
