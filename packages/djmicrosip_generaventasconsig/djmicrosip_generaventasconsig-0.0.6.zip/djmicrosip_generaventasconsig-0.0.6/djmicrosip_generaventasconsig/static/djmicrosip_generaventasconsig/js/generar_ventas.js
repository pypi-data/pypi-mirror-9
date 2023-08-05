$("input[name='select_all']").on("click", select_all);
$("input[type='checkbox'][name='documento']").on("click", mostrar_selecionados );

function select_all(){
  var to_select = this.checked;
  documentos = $("input[type='checkbox'][name='documento']");
  documentos.each(function(){
    this.checked = to_select;
  });
  mostrar_selecionados();
}

function mostrar_selecionados(){
  var selecionados = $("input[type='checkbox'][name='documento']:checked").length;
  if (selecionados > 0) {
    $("#selected_documents_count").text("  "+selecionados + " documentos selecionados.");
  }else{
    $("#selected_documents_count").text("");
  }
}


$("#btn_traspasarFacturas").on("click", function(){
  if ( $("#btn_traspasarFacturas").attr("disabled") == "disabled")
    return false
  $("#btn_traspasarFacturas").attr("disabled",'disabled');
  
  var documentos_selecionados = $("input[type='checkbox'][name='documento']:checked").map(function() {return this.value;}).get();
  documentos_selecionados = documentos_selecionados.join(",");
  $.ajax({
    url:'/generaventasconsig/generar_venta_de_facturas/', 
    type : 'get', 
    data:{
      'documentos_ids': documentos_selecionados,
    }, 
    success: function(data){
      var msg = data.msg + "\n";
      if (data.errors.length > 0){
        msg += data.errors; 
      }else{
        msg += '\n'+'IMPORTANTE: \n'+'Recuerda hay que modificar y guardar la venta (Para generar impuestos correctamente) y SOLO despues imprimir la factura'
      }
      
      alert(msg);
      location.reload();
    },
    error: function() {
      alert('fallo algo');
    },
  });
});

