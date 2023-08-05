
$("input[name='select_all']").on("click", sellect_all);
function sellect_all(){
  var to_select = this.checked;
  documentos = $("input[type='checkbox'][name='documento']");
  documentos.each(function(){
    this.checked = to_select;
    mostrar_selecionados();
  });
}

function mostrar_selecionados(){
  var selecionados = $("input[type='checkbox'][name='documento']:checked").length

  if (selecionados > 0) {
    $("#selected_documents_count").text(" "+selecionados + " documentos selecionados.");
  }else{
    $("#selected_documents_count").text("");
  }
}

$("input[type='checkbox'][name='documento']").on("click", mostrar_selecionados );

$("#btn_generarFacturas").on("click", function(){
  if ( $("#btn_generarFacturas").attr("disabled") == "disabled")
    return false
  $("#btn_generarFacturas").attr("disabled",'disabled');
  
  var documentos_selecionados = $("input[type='checkbox'][name='documento']:checked").map(function() {return this.value;}).get();
  $.ajax({
    url:'/djmicrosip_faexist/generar_compras/', 
    type : 'get', 
    data:{
      'documentos_ids': documentos_selecionados,
    }, 
    success: function(data){
      var msg = data.msg + "\n";
      if (data.errors.length > 0){
        msg += data.errors; 
      }
      alert(msg);
      location.reload();
    },
    error: function() {
      alert('fallo algo');
    },
  });
});


$("#selected_documents_count").text("");