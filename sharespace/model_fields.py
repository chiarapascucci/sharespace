from django.db import models

# cfrom phonenumber_field.modelfields import PhoneNumberField


class EmailFieldLowerCase (models.EmailField):
    def to_python(self, value):
        value = super(EmailFieldLowerCase, self).to_python(value)
        if isinstance(value, str):
            return value.lower()
        return value
