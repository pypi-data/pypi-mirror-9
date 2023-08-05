from django.db import models
# Create your models here.
from django_microsip_base.libs.models_base.models import (
	Articulo, ArticuloPrecio, LineaArticulos, PuntoVentaDocumento, Cliente, LineaArticulos, ClienteClave,
	PuntoVentaDocumentoDetalle, ClienteDireccion, PuntoVentaCobro, Moneda, ArticuloClave,
	ArticuloDiscreto, ArticuloDiscretoExistencia, PuntoVentaArticuloDiscreto, CajaMovimiento,TipoCambio, 
	CajeroCaja, ConexionDB, Proveedor, Registry,
	ComprasDocumento, ComprasDocumentoDetalle, Almacen, ArticuloClave, CuentasXPagarCondicionPagoPlazo, ComprasDocumentoCargoVencimiento)