#encoding:utf-8
from django import forms
import autocomplete_light
from .models import *
import autocomplete_light
from datetime import datetime
from microsip_api.comun.sic_db import first_or_none
from django.conf import settings

class PuntoVentaDocumentoForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(Cliente.objects.all(),widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'), required=True)
    linea = forms.ModelChoiceField(LineaArticulos.objects.all(),widget=autocomplete_light.ChoiceWidget('LineaArticulosAutocomplete'), required=True)
    
    def clean(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        
        cajero = cleaned_data.get('cajero')
        caja = cleaned_data.get('caja')
        
        if cajero and not cajero.operar_cajas == 'T' and not CajeroCaja.objects.filter(cajero=cajero, caja=caja).exists():
            raise forms.ValidationError(u'La caja [%s] no puede ser operada por el cajero [%s]'%(caja, cajero))
        
        
        apertura_ultima = first_or_none( CajaMovimiento.objects.filter(caja=caja, movimiento_tipo = 'A').order_by('-fecha','-hora'))
        cierre = None
        if apertura_ultima:
            #
            cierre = first_or_none( CajaMovimiento.objects.filter(caja=caja, movimiento_tipo = 'C', fecha__gte=apertura_ultima.fecha, hora__gt=apertura_ultima.hora.strftime('%H:%M:%S') ))

        if not caja:
            raise forms.ValidationError(u'Selecciona una caja')

        if not apertura_ultima or cierre and caja:
            raise forms.ValidationError(u'la caja %s no esta abierta por favor abrela para continuar.'%caja.nombre)

        return cleaned_data
    
    class Meta:
        model = PuntoVentaDocumento
        fields = ['cliente', 'caja','cajero', 'almacen']


class PreferenciasManageForm(forms.Form):
    periodo_fecha_inicio = forms.DateField()
    proveedor = forms.IntegerField(widget=forms.HiddenInput())
    almacen = forms.IntegerField(widget=forms.HiddenInput())
    cliente = forms.ModelChoiceField(Cliente.objects.all(),widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'), required=True)
    
    def __init__(self,*args,**kwargs):
        bases_de_datos = settings.MICROSIP_DATABASES.keys()
        empresas = []
        for database_conexion in bases_de_datos:
            try:
                database_conexion = u'%s'%database_conexion
            except UnicodeDecodeError:
                pass
            else:
                
                conexion_id, empresa = database_conexion.split('-')
                conexion = ConexionDB.objects.get(pk=int(conexion_id))
                database_conexion_name = "%s-%s"%(conexion.nombre, empresa)

                empresa_option = [database_conexion, database_conexion_name]
                empresas.append(empresa_option)
                        
        super(PreferenciasManageForm,self).__init__(*args,**kwargs)
        self.fields['database'] = forms.ChoiceField(choices= empresas)
        