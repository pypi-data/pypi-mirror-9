from django.conf.urls import patterns, url
from .views import index, exporta_factura,preferencias, GetProveedoresByEmpresa, GuardarPreferencias, GenerarCompras, GetAlmacenesByEmpresa, UpdateDatabaseTable

urlpatterns = patterns('',
	(r'^$', index),
	(r'^exporta_factura/$', exporta_factura),
	(r'^preferencias/$', preferencias),
	# AJAX
	(r'^get_proveedores_byempresa/$', GetProveedoresByEmpresa),
	(r'^get_almacenes_byempresa/$', GetAlmacenesByEmpresa),
	(r'^guardar_preferencias/$', GuardarPreferencias),
	(r'^generar_compras/$', GenerarCompras),
	(r'^preferencias/actualizar_tablas/$', UpdateDatabaseTable),
	
	
	
)

