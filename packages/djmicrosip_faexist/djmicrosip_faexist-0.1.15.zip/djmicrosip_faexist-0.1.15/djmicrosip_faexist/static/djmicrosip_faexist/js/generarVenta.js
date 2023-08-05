
$("#btn_generarVenta").on("click", function(){
	var linea_id = $("#id_linea").val();
	var cliente_id = $("#id_cliente").val();
	debugger;
  if ( linea_id == null )
  {
    alert("Por favor indica la linea");
	return false;
  }
  if (cliente_id == null )
  {
    alert("Por favor indica el cliente");
	return false;
  }
  if (linea_id != null && cliente_id != null) {
  	$("#btn_generarVenta").hide();
  }
});
  
$("#btn_generarVenta").attr("disabled",false);