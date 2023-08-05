import autocomplete_light
from django_microsip_base.libs.models_base.models import LineaArticulos

autocomplete_light.register(
	LineaArticulos, 
	search_fields=('nombre',), 
	autocomplete_js_attributes={'placeholder': 'Linea ..', 'class':'form-control',}, 
	choices = LineaArticulos.objects.all(),
	name = 'LineaArticulosAutocomplete',
	)

