from django.db import models


class EmailFieldLowerCase (models.EmailField):
    def to_python(self, value):
        value = super(EmailFieldLowerCase, self).to_python(value)
        if isinstance(value, str):
            return value.lower()
        return value
