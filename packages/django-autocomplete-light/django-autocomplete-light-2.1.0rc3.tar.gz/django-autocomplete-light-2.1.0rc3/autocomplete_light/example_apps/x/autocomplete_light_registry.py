import autocomplete_light.shortcuts as autocomplete_light
from .models import Company, Customer


class BaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    pass


class CustomerAutocomplete(BaseAutocomplete):
    search_fields = ['name']
    model = Company
    choices = Company.objects.all()
autocomplete_light.register(CustomerAutocomplete)
