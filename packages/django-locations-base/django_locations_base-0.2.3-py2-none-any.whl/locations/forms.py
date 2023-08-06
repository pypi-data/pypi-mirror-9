from django import forms

from locations.models import Location


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = ('',)