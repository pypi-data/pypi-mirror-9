function getProveedores(){
  var empresa_nombre = $("#id_database").val();
  $.ajax({
    url:'/djmicrosip_faexist/get_proveedores_byempresa/', 
    type : 'get', 
    data:{
      'empresa_conexion': empresa_nombre,
    }, 
    success: function(data){
      $("#id_proveedores").html('');
      $("#id_proveedores").append("<option value=''>Seleciona un proveedor </option>");
      data.proveedores.forEach(function(proveedor){
        $("#id_proveedores").append("<option value="+ proveedor.id +">"+ proveedor.nombre+"</option>");
      });

      if ($("#id_proveedor").val() != "" ){
        $("#id_proveedores").val($("#id_proveedor").val());
      }
    },
    error: function() {
      alert('fallo algo');
    },
  });
}

function getAlmacenes(){
  var empresa_nombre = $("#id_database").val();
  $.ajax({
    url:'/djmicrosip_faexist/get_almacenes_byempresa/', 
    type : 'get', 
    data:{
      'empresa_conexion': empresa_nombre,
    }, 
    success: function(data){
      $("#id_almacenes").html('');
      $("#id_almacenes").append("<option value=''>Seleciona un almacen </option>");
      data.almacenes.forEach(function(almacen){
        $("#id_almacenes").append("<option value="+ almacen.ALMACEN_ID +">"+ almacen.nombre+"</option>");
      });

      if ($("#id_almacen").val() != "" ){
        $("#id_almacenes").val($("#id_almacen").val());
      }
    },
    error: function() {
      alert('fallo algo');
    },
  });
}

$("#id_database").on("change", function(){
  $("#id_proveedor").val("");
  $("#id_almacen").val("");
  getProveedores(); 
  getAlmacenes();
});

$("#id_proveedores").on("change", function(){
  var selected_proveedor =  $("#id_proveedores").val();
  $("#id_proveedor").val(selected_proveedor);
});

$("#id_almacenes").on("change", function(){
  var selected_almacen =  $("#id_almacenes").val();
  $("#id_almacen").val(selected_almacen);
});

function validForm(){
  if ($("#id_periodo_fecha_inicio").val() == null || $("#id_periodo_fecha_inicio").val() == "" ) {
    alert("Campo fecha requerido");
    return false
  }

  if ($("#id_cliente").val() == null) {
    alert("Campo cliente factura requerido");
    return false
  }

  if ($("#id_database").val() == null) {
    alert("Campo empresa requerido");
    return false
  }

  if ($("#id_proveedor").val() == '') {
    alert("Campo proveedor requerido");
    return false
  }

  if ($("#id_almacen").val() == '') {
    alert("Campo almacen requerido");
    return false
  }

  return true;
}

$("#id_btn_save").on("click", function(){
  busqueda_fecha_inicio = $("#id_periodo_fecha_inicio").val();
  busqueda_cliente_facturas_id = $("#id_cliente").val();
  compras_empresa_id = $("#id_database").val();
  compras_proveedor_id = $("#id_proveedor").val();
  compras_almacen_id = $("#id_almacen").val();
  
  if (validForm()){
    $.ajax({
      url:'/djmicrosip_faexist/guardar_preferencias/', 
      type : 'get', 
      data:{
        'busqueda_fecha_inicio': busqueda_fecha_inicio,
        'busqueda_cliente_facturas_id': busqueda_cliente_facturas_id,
        'compras_proveedor_id': compras_proveedor_id,
        'compras_empresa_id': compras_empresa_id,
        'compras_almacen_id':compras_almacen_id,
      }, 
      success: function(data){
        alert(data.msg);
      },
      error: function() {
        alert('fallo algo');
      },
    }); 
  }

});

getProveedores();
getAlmacenes();