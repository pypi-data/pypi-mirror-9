from django.utils.translation import ugettext_lazy as _
from rest_framework import validators
from rest_framework.exceptions import ValidationError


class UniqueValidator(validators.UniqueValidator):
    """
    Validator that corresponds to `unique=True` on a model field.

    Should be applied to an individual field on the serializer.
    """
    def __call__(self, value):
        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset)
        queryset = self.exclude_current_instance(queryset)
        if queryset.first():
            raise ValidationError(self.message)


class UniqueTogetherValidator(validators.UniqueTogetherValidator):
    """
    Validator that corresponds to `unique_together = (...)` on a model class.

    Should be applied to the serializer class, not to an individual field.
    """
    def __call__(self, attrs):
        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset)
        queryset = self.exclude_current_instance(attrs, queryset)
        if queryset.first():
            field_names = ', '.join(self.fields)
            raise ValidationError(self.message.format(field_names=field_names))


class BaseUniqueForValidator(validators.BaseUniqueForValidator):
    def __call__(self, attrs):
        self.enforce_required_fields(attrs)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset)
        queryset = self.exclude_current_instance(attrs, queryset)
        if queryset.first():
            message = self.message.format(date_field=self.date_field)
            raise ValidationError({self.field: message})


class UniqueForDateValidator(BaseUniqueForValidator):
    message = _('This field must be unique for the "{date_field}" date.')

    def filter_queryset(self, attrs, queryset):
        value = attrs[self.field]
        date = attrs[self.date_field]

        filter_kwargs = {}
        filter_kwargs[self.field_name] = value
        filter_kwargs['%s__day' % self.date_field_name] = date.day
        filter_kwargs['%s__month' % self.date_field_name] = date.month
        filter_kwargs['%s__year' % self.date_field_name] = date.year
        return queryset.filter(**filter_kwargs)


class UniqueForMonthValidator(BaseUniqueForValidator):
    message = _('This field must be unique for the "{date_field}" month.')

    def filter_queryset(self, attrs, queryset):
        value = attrs[self.field]
        date = attrs[self.date_field]

        filter_kwargs = {}
        filter_kwargs[self.field_name] = value
        filter_kwargs['%s__month' % self.date_field_name] = date.month
        return queryset.filter(**filter_kwargs)


class UniqueForYearValidator(BaseUniqueForValidator):
    message = _('This field must be unique for the "{date_field}" year.')

    def filter_queryset(self, attrs, queryset):
        value = attrs[self.field]
        date = attrs[self.date_field]

        filter_kwargs = {}
        filter_kwargs[self.field_name] = value
        filter_kwargs['%s__year' % self.date_field_name] = date.year
        return queryset.filter(**filter_kwargs)
