var SHOW_MOBILE = false;
$("#id_articulo_text, #id_articulo_serie_text").addClass('form-control');
$("#articuloContainerSerie").hide();
var $articulo = $("#id_articulo");
var $hidden_articulo = $("#id_articulo_serie");
var manejarSeries = $("#manejarSeries")[0].checked;
var modoRapido =  $('#chbx_modorapido')[0].checked;
var $articulo_clave = $("#id_clave_articulo");
var $articulo_serie = $("#serieArticuloId");
var es_small = $("#extra_mobile_btn:visible").length>0;

// ------------------FUNCIONES---------------------
// *******************COMUN *************************
/* Funcion para mostrar constroles para series */
function mostrarControles(){ 
  if($("#extra_mobile_btn:visible").length>0){  
    modoRapido = $('#chbx_modorapido')[0].checked;
  }
  else{
   modoRapido = false;
  }
  manejarSeries = $("#manejarSeries")[0].checked;
  $articulo.parent().find(".deck.div").find(".remove").trigger("click");


  $("#id_unidades, #unidades_div").hide();
  $("#articleDetailId").hide();
  if(manejarSeries)
  {
    $articulo = $("#id_articulo_serie");
    $hidden_articulo = $("#id_articulo");
    $("#serieArticuloId").parent().show();
    $("#id_clave_articulo, .ajustarPrimerConteoContainer").hide();
    $("#serieArticuloId").focus();
  /* Si se manejan articulos normales */
  }
  else
  {
    $hidden_articulo = $("#id_articulo_serie");
    $articulo = $("#id_articulo");

    $(".ajustarPrimerConteoContainer").show();
    $("#serieArticuloId").parent().hide();
    /* Si es modo rapido */
    if(modoRapido)
    {

      $("#id_clave_articulo").show();
      if (es_small)
      {
        $articulo.parent().hide();
      }

      $("#id_clave_articulo").focus();
    }
    else
    {
      $articulo.parent().show();
      $("#id_clave_articulo").hide();
      $articulo.focus();
    }

    // Si no se carga version mobile muestro tambien clave
    if($("#extra_mobile_btn:visible").length==0)
    {
      $("#id_articulo_text, #id_clave_articulo").show();
      $articulo.parent().show();
    }
  }
  // $articulo.parent().show();
  $hidden_articulo.parent().hide();
  $hidden_articulo.parent().find("input").hide();
}
mostrarControles();

// Carga las opciones de clave
function cargar_opciones_clave(opciones){

  if (Object.keys(opciones).length > 0 ) {
    html_var = '';
    for (articulo in opciones)
    { 
      html_var = html_var + "<a href='#' class='clave_link'>" + articulo + "</a> " + opciones[articulo]+"<br>";
    }

    $("#opciones_clave_Modal").modal();
    $("#id_opciones_clave").html(html_var);
    $(".clave_link").on("click", function(){
      $("#id_clave_articulo").val($(this).text());
      $("#id_clave_articulo").trigger('change');
      $('#opciones_clave_Modal').modal('hide');
    });
  }
}

// Funcion que carga el articulo seleccionado en autocomplete
function cargar_articulo( articulo_id, articulo_nombre, tipo_seguimiento){  
  $articulo.parent().find(".deck.div").attr('style','');
  $articulo.parent().find(".deck.div").html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
  $articulo.html('<option selected="selected" value="'+articulo_id+'"></option>');
  $("#articuloSeguimientoUnidadesId").val(tipo_seguimiento);
  $articulo.parent().find("input").hide();
  $articulo.trigger( "change" );
  $articulo.parent().show();
  $articulo.parent().parent().show();
  if (manejarSeries == false) {
    $("#id_unidades").show();
    $("#id_unidades").focus();
  }
}

// Agrega existencias al articulo
function add_existenciasarticulo_byajuste(){
  if ( $("#enviar_btn").attr("disabled") == "disabled")
    return false

  var $ubicacion = $('#ubicacion');

  if ($ubicacion.val() == ''){
      alert("El campo ubicacion es obligatorio");
      if ($("#extra_mobile_btn:visible").length>0){
        $("#extra_mobile_btn").trigger("click");
      }

      $ubicacion.focus();
      return;
  }
  else if ($articulo.find("option:selected").val() == undefined)
  {
    alert("El campo articulo es obligatorio");
    $articulo.parent().find("input").focus();
    return;
  }
  else if ($('#id_unidades').val() == '')
  { 

    alert("El campo unidades es obligatorio");
    $("#id_unidades").show();
    $("#id_unidades").focus();
    return;
  }
  else if ($.isNumeric($('#id_unidades').val()) == false )
  {
    $("#id_unidades").show();
    alert("Unidades incorrectas");
    $("#id_unidades").focus();
    return;
  }
  
  var entrada_id  = $("#hidden_entrada_id").val();
  var salida_id = $("#hidden_salida_id").val();
  var ubicacion = $ubicacion.val();
  var unidades = $("#id_unidades").val();
  // var costo_unitario = $('#id_costo_unitario').val();
  var articulo_id = $articulo.val()[0];
  var almacen_nombre =  $("#almacen_nombre").val();
  var tipo_seguimiento = $("#articuloSeguimientoUnidadesId").val();

  data = {
    'entrada_id':entrada_id,
    'salida_id':salida_id,
    'ubicacion':ubicacion,
    'unidades':unidades,
    'costo_unitario':0,
    'articulo_id':articulo_id,
    'almacen_nombre':almacen_nombre,
    'tipo_seguimiento': tipo_seguimiento
  }
  if (tipo_seguimiento == 'S'){
    data.serie =  $("#serieArticuloId").val();
  }

  $("#enviar_btn").attr("disabled",true);
  $.ajax({
      url:'/inventarios/agregar_existencia/', 
      type : 'get', 
      data:data, 
      success: function(data){
        
        var $articulo_tr = $("#articulo-"+data.articulo_id).parent().parent();
        var contenido_existencia = data.existencia;
        var span_class_name;

        if (data.tipo_seguimiento=='S') {
          var span_class_name = "seriesSinContar";
          if (data.series_por_contar<=0) {
            span_class_name = "seriesContadas";
          }
          contenido_existencia += " <a href='#'> <span class='badge "+span_class_name+"'>Faltan "+data.series_por_contar+"</a>"
        };
        
        // Cuando ya existe en la tabla
        if ($articulo_tr.length>0)
        {
          $articulo_tr.children(":last").html(contenido_existencia);
          var temp = $articulo_tr.addClass("warning")[0]
          $articulo_tr.remove();
          $("#ultimos_articulos_contados tbody").prepend(temp);
        }
        // Si no existe en tabla
        else
        {  
          var contados = parseInt($("#articulosContadosId").text()) + 1;
          $("#articulosContadosId").text(contados);
          $articulo_tr = "<tr class='warning'><td>"+data.articulo_clave+"<input type='hidden' id='articulo-"+data.articulo_id +"' value='"+data.articulo_id+"'/> </td><td>"+data.articulo_nombre+"</td><td>"+contenido_existencia+"</td></tr>"
          $("#ultimos_articulos_contados tbody").prepend($articulo_tr);
        }

        if (data.tipo_seguimiento=='S') 
        {  
          startSeriesAddEvents($articulo_tr, span_class_name, span_class_name);
        }
        $articulo.parent().find(".deck.div").find(".remove").trigger("click");
        
        if($("#extra_mobile_btn:visible").length>0)
        {
          if($("#chbx_modorapido:checked").length>0)
          {
            $("#id_clave_articulo").show();
            $("#id_clave_articulo").focus();
            $articulo.parent().find("input").hide();
          }
          else
          {
            $articulo.parent().find("input").show();
            $articulo.parent().find("input").focus();
            $("#id_clave_articulo").hide();
          }
        }

        if (es_small)
        {
          $articulo.parent().hide();
        }
        else
        {
          $articulo_clave.show();
        }

        if (manejarSeries) 
        {
          $articulo_serie.focus();
          $articulo.parent().hide(); 
          $articulo_clave.hide();
        }
        else
        {
          if (modoRapido && es_small)
          {  
            $articulo_clave.show();
          }
          
          if (modoRapido)
          {
            $articulo_clave.focus();
          }
          else
          {
            $articulo.parent().show();
            $articulo.parent().find("input").focus();
          };
        };
        $("#enviar_btn").attr("disabled",false);
        if (es_small)
        {
          $("body").scrollTop(100);
        }
      },error: function() {
        alert('fallo algo');
      },
    });
}

// *******************SERIES*********************
// Funcion muestra opciones con numeros de serie
function cargarOpcionesSerie(opciones){
  html_var = '';

  for (articulo in opciones)
  { 
    html_var = html_var + "<a href='#' class='serie_link'><input type='hidden' value='"+articulo+"'/>" + opciones[articulo] + "</a><br>";
  }

  $("#opciones_clave_Modal").modal();
  $("#id_opciones_clave").html(html_var);
  $(".serie_link").on("click", function(){
    var articulo_id = $(this).find("input").val();
    var articulo_nombre = $(this).text();
    cargar_articulo(articulo_id, articulo_nombre, 'S');
    $('#opciones_clave_Modal').modal('hide');
  });
}

// Muestra las series que no han sido contadas
function mostrarPorContar(articulo_id, almacen_nombre){
  $.ajax({
    url:'/inventarios/get_series_porcontar/', 
    type : 'get', 
    data:{
      'articulo_id': articulo_id,
      'almacen_nombre':almacen_nombre
    }, 
    success: function(data){
      var message = "Faltan de contar las siguientes series\n";
      for(serie in data.series){
        message += data.series[serie] + "\n"
      }

      alert(message);
    },
    error: function() {
      alert('fallo algo');
    },
  });
}

function mostrarSeriesContadas(articulo_id, almacen_nombre){
  $.ajax({
    url:'/inventarios/get_series_contadas/', 
    type : 'get', 
    data:{
      'articulo_id': articulo_id,
      'almacen_nombre':almacen_nombre
    }, 
    success: function(data){
      var message = "Series contadas\n";
      for(serie in data.series){
        message += data.series[serie] + "\n"
      }

      alert(message);
    },
    error: function() {
      alert('fallo algo');
    },
  });
}
// ------------------FIN FUNCIONES---------------------

// ----------------EVENTOS--------------------------------------------------------
// *******************MOBILE*****************************************************
$('#manejarSeriesMobil').on("change", function(){
  manejarSeries = this.checked;
  $("#manejarSeries")[0].checked = manejarSeries;
  $("#manejarSeries").trigger("change");
});

$('#ubicacionMobil').on("change", function(){
  $("#ubicacion").val(this.value);
  $("#ubicacion").trigger("change");
});

$("#extra_mobile_btn").on("click", function(){
  if (SHOW_MOBILE == false){
    $("#extra_mobile").show();
    SHOW_MOBILE = true;
  }else{
    $("#extra_mobile").hide();
    SHOW_MOBILE = false;
  }
});

// *******************COMUN**************************************************
$('#chbx_modorapido, #manejarSeries').on("change", function(){
  mostrarControles();
});

$("#id_articulo_text, #id_articulo_serie_text").on("click",function(){
  modoRapido = false;
  if (es_small)
  {
    $("body").scrollTop(100);
  }
});

$("#cancel_btn").on("click", function(){
  $articulo.parent().find(".deck.div").find(".remove").trigger("click");
});

function detalle_movimientos()
{
  
  $.ajax({
    url:'/inventarios/get_movimientos_articulo/', 
    type : 'get', 
    data:{
      'almacen_id' : $("#almacen_id").val(),
      'articulo_id': $articulo.val()[0],
    }, 
    success: function(data){
      var detalles = data.detalles;
      var articulo_nombre = $articulo.parent().find(".deck.div").children().contents()[1].data;
      
      $("#modalMovmentsTitle").html("<h4>"+articulo_nombre+"</h4>");
        
      var msg=  "<h4> Valores iniciales</h4> <strong>Existencia: </strong>"+ data.existencia_inicial+" <br/><h4> Movimientos</h4>\n <table class='table table-striped table-hover'><tr><th>Usuario/Ubicacion</th><th>Unidades</th><th>fecha</th></tr>";
      for(detalle in detalles){
        msg += "<tr><td>"+detalles[detalle].usuario+"/"+detalles[detalle].ubicacion+"</td><td>"+ detalles[detalle].unidades +'</td><td>' +detalles[detalle].fechahora+'</td></tr>';
      }
      msg+="</table>"
      $("#movimiento_articulo_modal .modal-body").html(msg);
      $("#movimiento_articulo_modal").modal();
    },
    error: function() {
      alert('algo fallo');
    },
  });  
  
}

/* Mostrar articulo */
$("#id_articulo, #id_articulo_serie").on("change", function(){
  // Si no hay articulo seleccionado
  if( $articulo.val() == null )
  {
    $("#articleDetailId").hide();
    $('#unidades_div').hide();
    $("#id_clave_articulo, #serieArticuloId").val('');
    $articulo_serie.attr("disabled",false);
    if (manejarSeries)
    {
      $articulo_serie.focus();
      $articulo.parent().hide();
    }
    $("#id_unidades").val('');
  }
  // Si hay articulo seleccionado
  else
  {
    $('#unidades_div').show();
    $("#id_clave_articulo").hide();
    var serie = $("#serieArticuloId").val();
    var data = {
      'almacen': $("#almacen_nombre").val(), 
      'articulo_id': $articulo.val()[0],
      'serie': serie,
    }
    $.ajax({
      url:'/inventarios/get_existencia_articulo/', 
      type : 'get', 
      data: data, 
      success: function(data){
        tipo_seguimiento = data.articulo_seguimiento;
        var ya_ajustado = data.ya_ajustado;
        $("#articuloSeguimientoUnidadesId").val(tipo_seguimiento);
        if (tipo_seguimiento == 'S' && ya_ajustado) 
        {
          $articulo.parent().find(".deck.div").find(".remove").trigger("click");
          $articulo.parent().parent().hide();
          $articulo_serie.focus();
          alert('Serie ya contada en el inventario');
        }
        else
        {
          var detalle_movimientos_link="";
          if (ya_ajustado)
          {
            detalle_movimientos_link = "<a tabindex='-1' id='id_detalle_movimientos' href='#' role='button' data-toggle='modal'><i class='glyphicon glyphicon-info-sign icon-white'></i></a>";
          }
          $('#span_alerta_unidades').html(data.existencias + " en existencia. "+detalle_movimientos_link);
          $("#id_detalle_movimientos").on("click", detalle_movimientos);
          $('#articleDetailId').show();
          var por_contar = "";
          $('#unidades_div, #id_unidades').show();

          if (es_small) 
          {
            $("#cancel_btn").show();
          }
          else
          {
            $("#cancel_btn").hide();
          }
          $(".articleOptions").show();
          if (tipo_seguimiento == 'S') 
          {
            $articulo_serie.attr("disabled",true);
            por_contar = "<a href='#''><span class='badge' id='porContar'>"+data.series_faltantes+"</span></a>"
            $("#id_unidades").val('1');
            $("#id_unidades").hide();
          }
          else if(tipo_seguimiento  == 'N')
          {
            $("#id_unidades, #id_costo_unitario").val('');
            $("#id_unidades").show();
            $("#id_unidades").focus();
          }
          
          if (ya_ajustado == true)
          {
            $('#spanEstadoConteo').attr("class","yaContado");
            $("#spanEstadoConteo").html("Ya contado "+ por_contar);
          }
          else
          {
            // $('#spanEstadoConteo').addClass("sinContar");
            $('#spanEstadoConteo').attr("class","sinContar");
            $("#spanEstadoConteo").html("Sin contar "+por_contar);
          }

          $("#porContar").on("click", function(){
            var articulo_id = $articulo.val();
            var almacen_nombre = $("#almacen_nombre").val();
            mostrarPorContar(articulo_id, almacen_nombre);
          });

          if (es_small) 
          {
            $("body").scrollTop(100);
          }

        }
      },
      error: function() {
        alert('fallo algo');
      },

    });
  }
});

// Busca las claves de Articulos y muestra opciones
$("#id_clave_articulo").on("change", function(e){
  e.preventDefault();
  modoRapido = true;
  clave = $("#id_clave_articulo").val();
  if( clave != null && clave != '' ){
    $.ajax({
      url:'/inventarios/get_articulo_porclave/', 
      type : 'get', 
      data:{
        'clave': clave,
      }, 
      success: function(data){
          var opciones_clave =  data.opciones_clave;
          var articulo_nombre = data.articulo_nombre;
          var articulo_id = data.articulo_id;
          if (Object.keys(opciones_clave).length <= 0)
          {
            if (articulo_nombre == '')
            {
              alert('No se encontro ningun articulo con la clave');
            }
            else
            {
              cargar_articulo(articulo_id, articulo_nombre, 'N');
            }
          // Si hay opciones por mostrar
          }
          else
          {
            cargar_opciones_clave(opciones_clave);
          }
      },
      error: function() {
        alert('fallo algo');
      },
    });
  }
  return false;
});

$("#enviar_btn").on("click", function(){
  add_existenciasarticulo_byajuste();
});

// *******************SERIES*****************************************************
// Muestra series sin contar en la lista de ultimos articulos ingresados

function startSeriesAddEvents($element, span_class_name){
  debugger;
  if (span_class_name=="seriesSinContar")
  {
    $element.find(".badge.seriesSinContar").on("click", function(){ 
      var articulo_id = $(this).parent().parent().parent().find("input:hidden").val();
      var almacen_nombre = $("#almacen_nombre").val();
      mostrarPorContar(articulo_id, almacen_nombre)
    });
  }
  else if (span_class_name=="seriesContadas")
  {
    $element.find(".badge.seriesSinContar").on("click", function(){ 
      var articulo_id = $(this).parent().parent().parent().find("input:hidden").val();
      var almacen_nombre = $("#almacen_nombre").val();
      dynamicfunction(articulo_id, almacen_nombre)
    });
  }
}

function startSeriesEvents(){
  $(".badge.seriesSinContar").on("click", function(){ 
    var articulo_id = $(this).parent().parent().parent().find("input:hidden").val();
    var almacen_nombre = $("#almacen_nombre").val();
    mostrarPorContar(articulo_id, almacen_nombre);
  });

  $(".badge.seriesContadas").on("click", function(){ 
    var articulo_id = $(this).parent().parent().parent().find("input:hidden").val();
    var almacen_nombre = $("#almacen_nombre").val();
    mostrarSeriesContadas(articulo_id, almacen_nombre);
  });
}
startSeriesEvents();
/* Busca articulo por serie si no existe da opcion de indicar un articulo
   si hay varias opcines muestra para seleccionar.*/
$("#serieArticuloId").on("change", function(e){
  e.preventDefault();
  serie = $("#serieArticuloId").val();
  if( serie != null && serie != '' )
  {
    $.ajax({
      url:'/inventarios/get_articulo_porserie/', 
      type : 'get', 
      data:{
        'almacen_id':$("#almacen_id").val(),
        'serie': serie,
      },
      success: function(data){
          if (data.errors)
          {
            // FALTA dar opcion de selecionar articulo
            alert(data.errors);
            $articulo.parent().show();
            $articulo.parent().parent().show();
            $articulo.parent().find("input").focus();
          }
          else if(data.opciones)
          {
            cargarOpcionesSerie(data.opciones);
          }
          else
          {
            cargar_articulo(data.articulo_id, data.articulo_nombre, 'S');
          }
      },
      error: function() {
        alert('fallo algo');
      },
    });
  }
  return false;
});


// ---------------- FIN EVENTOS--------------------------------------------------------

function cerrar_inventario(){
  $.ajax({
      url:'/inventarios/close_inventario_byalmacen_view/', 
      type : 'get', 
      data:{
        'almacen_id' : $("#almacen_id").val(),
      }, 
      success: function(data){ 
        alert(data.mensaje);
        window.location = "/inventarios/almacenes/";
      },
      error: function() {
        },
    });  
}

function mostrar_articulos_agregados(data)
{
  if (data.articulos_agregados > 0)
  {
    mensaje ='Se agregaron '+ data.articulos_agregados+ ' Articulos'
    if (data.articulo_pendientes > 0)
      mensaje = 'La aplicacion solo genero ' + data.articulos_agregados+ ' Articulos, faltaron de generar '+data.articulo_pendientes + ' Articulos.'
    alert(mensaje);
  }
  else
  {
    if (data.message != '')
      alert(data.message);
    else
      alert('No hay articulos por inicializar');
  }
}

function agregar_articulos_fn()
{
  if ( $("#btn_agregar_articulosinexistencia").attr("disabled") == "disabled")
    return false

   $.ajax({
      url:'/inventarios/add_articulossinexistencia/', 
      type : 'get', 
      data:{
        'ubicacion' : $("#ubicacion").val(),
        'almacen_id' : $("#almacen_id").val(),
      }, 
      success: mostrar_articulos_agregados,
      error: function() {
        },
    });  

  $('#btn_agregar_articulosinexistencia').hide();
  // $('#btnCancel').hide();
  $("#btn_agregar_articulosinexistencia").attr("disabled",true);
  $("#id_agregando_span_all").show();
}





