
$("input[name='select_all']").on("click", sellect_all);
function sellect_all(){
  var to_select = this.checked;
  documentos = $("input[type='checkbox'][name='articulos']");
  documentos.each(function(){
    this.checked = to_select;
    mostrar_selecionados();
  });
}

function mostrar_selecionados(){
  var selecionados = $("input[type='checkbox'][name='articulos']:checked").length

  if (selecionados > 0) {
    $("#selected_objects").text(" "+selecionados + " objetos selecionados.");
    $("#btn_acciones").show();
  }else{
    $("#selected_objects").text("");
    $("#btn_acciones").hide();
  }
}

$("input[type='checkbox'][name='articulos']").on("click", mostrar_selecionados );

$("#btnIgnorarArticulos").on("click", function(){
  if ( $("#btnIgnorarArticulos").attr("disabled") == "disabled")
    return false
  $("#btnIgnorarArticulos").attr("disabled",'disabled');
  
  var articulos_ids = $("input[type='checkbox'][name='articulos']:checked").map(function() {return this.value;}).get();
  
  $.ajax({
    url:'/djmicrosip_faexist/ignorar_articulos/', 
    type : 'get', 
    data:{
      'articulos_ids': articulos_ids,
      'ignorar': true,
    }, 
    success: function(data){
      // var msg = data.msg + "\n";
      // if (data.errors.length > 0){
      //   msg += data.errors; 
      // }
      // alert(msg);
      location.reload(true);
    },
    error: function() {
      alert('fallo algo');
    },
  });
});


$("input[type='checkbox'][name='articulos']").on("click", mostrar_selecionados );

$("#btnNoIgnorarArticulos").on("click", function(){
  if ( $("#btnNoIgnorarArticulos").attr("disabled") == "disabled")
    return false
  $("#btnNoIgnorarArticulos").attr("disabled",'disabled');
  
  var articulos_ids = $("input[type='checkbox'][name='articulos']:checked").map(function() {return this.value;}).get();
  
  $.ajax({
    url:'/djmicrosip_faexist/ignorar_articulos/', 
    type : 'get', 
    data:{
      'articulos_ids': articulos_ids,
      'ignorar': false,
    }, 
    success: function(data){
      // var msg = data.msg + "\n";
      // if (data.errors.length > 0){
      //   msg += data.errors; 
      // }
      // alert(msg);
      location.reload(true);
    },
    error: function() {
      alert('fallo algo');
    },
  });
});



$("#btn_acciones").hide();
$("#selected_objects").text("");