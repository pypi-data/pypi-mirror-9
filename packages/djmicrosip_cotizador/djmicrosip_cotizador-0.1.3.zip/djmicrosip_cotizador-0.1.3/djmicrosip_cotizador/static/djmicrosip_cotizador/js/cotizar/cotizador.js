var $total = $("#total");
var $subtotal = $("#subtotal");
var $descuento = $("#descuento");
var $descuentop = $("#descuentop");
var $descuento_tp = $("#descuento_tp");
var $total_con_descuento = $("#total_con_descuento");
var moneda_id = $("#select_monedas").val();
var lista_precios_id = $("#select_lista_precios").val();

$(document).ready(function(){
	$("#modal-button").attr("disabled",true);
	$(".sub").hide();
	$(".des").hide();
	$(".descuento_tp").hide();
	$(".total_con_descuento").hide();
	$("input[name*='-precio_total_neto']").attr("readonly","true");

	var estructura_id = $('#estructuraId').val();
	$.ajax({
		url:'/cotizador/cotizar/get_detalles/', 
	  type : 'get', 
	  data:{
	  	'estructura_id':estructura_id,
	  }, 
	  success: function(data){

	  	//  Para cargar estructura
	  	detalles = data.detalles;
		detalles.forEach(function(carpeta, index){
			var $tr = $( "#id_detalles_data tbody tr:last")	
			$('<tr class="encabezado-folder"><td colspan="7"><strong>'+ carpeta.carpeta__nombre +'</strong></td></tr>').insertBefore( $tr );
			if(index<detalles.length-1){
				$('.btn-success').click();
			}
			$unidades = $tr.find("input[name*='-unidades']")
			$tr.find('.delete-row').hide()
			var $articuloContainer = $tr.find(".articuloContainer")
			$articuloContainer.attr('class','col-lg-7 col-md-7 col-sm-7 col-xs-7 articuloContainer')
			$articuloContainer.parent().append('<div class="col-lg-1 col-md-1 col-sm-1 col-xs-1"><a href="#" class="btn detalle-btnBuscar"><i class="glyphicon glyphicon-search"></i></a><input type="hidden" value="'+carpeta.carpeta__id+'" class="encabezado-folderId" name="folders" id="estructura'+ carpeta.id +'" /></div>');
			$unidades.val(carpeta.cantidad)
		});
		var $tr = $( "#id_detalles_data tbody tr:last")
		$('<tr class="encabezado-folder"><td colspan="6"><strong>Otros</strong></td></tr>').insertAfter( $tr );

		// evento para buscar articulos segun estructura
		$(".detalle-btnBuscar").on("click", function(){
			var $tr = $(this).parent().parent().parent().parent()
			$("#selectedFolderId").val($tr.find(".encabezado-folderId").val())
			$articulo = $tr.find("input[name*='-articulo']")
			loadNodeTree($("#selectedFolderId").val(), $("#id_tree_container"))
			var folder_id = $("#selectedFolderId").val()
			lista_precios_id = $("#select_lista_precios").val()
			var nombre = $("#modal-nombre").val()
			var clave = $("#modal-clave").val()
			$("#modal_arbol").modal()
		});
	  },
	  error: function() {
	  	alert("error");
	  },
	});

});

function foco_detalle(){
	$("[name*='-unidades']").last().val(1);
	$("input[name*='-clave']").last().focus();
	$("input[name*='-precio_total_neto']").attr("readonly","true");
	$("[name*='-articulo-autocomplete']").attr("class","form-control");
	$(".delete-row").find("i").attr("class","glyphicon glyphicon-trash");
}

$("#descuentop").on("input",function(){
	if ($(this).val() == '') 
	{ 
		$(this).val(0);
		$(this).select();
	};
	var descuentop = parseFloat($("#descuentop").val());
	var subtotal = parseFloat($total.text());
	var descuento_tp = parseFloat(subtotal*descuentop/100);
	var total_con_descuento = parseFloat(subtotal-descuento_tp);
	$total_con_descuento.text(total_con_descuento.toFixed(2));
	$descuento_tp.text(descuento_tp.toFixed(2));

	if (total_con_descuento == subtotal)
	{
		$(".descuento_tp").hide();
		$(".total_con_descuento").hide();
	}
	else
	{
		
		$(".descuento_tp").show();
		$(".total_con_descuento").show();
	};
});

$("input").on("keypress", function(e) {
            /* ENTER PRESSED*/
        if (e.keyCode == 13) {
        	$(this).trigger( "focusout" );
        }
    });

$("input").on("focusin",function(){
	$(this).select();
});

//AL CAMBIAR LA MONEDA A MOSTRAR EN EL SELECT
$("#select_monedas").on("change",function(){	
	$("select[name*='-articulo']").trigger("change")
	if ($(this).val() == '-')
	{
		$(this).val(moneda_id);
	}
	$("#cotiza").show();
	foco_detalle();
	$("#id_tipo_cambio_d").attr("disabled",true);
	moneda_id = $(this).val();
	get_total();

});

//AL CAMBIAR LA LISTA DE PRECIOS
$("#select_lista_precios").on("change",function(){
	$("select[name*='-articulo']").trigger("change")
	
	if ($(this).val() == '-')
	{
		$(this).val(lista_precios_id);
	}
	else
	{
		$("#modal-button").attr("disabled",false);
	};
	lista_precios_id = $(this).val();	
	
});

// para calcular totales
$("[name*='-precio_unitario'], [name*='-unidades'], [name*='-descuento']").on("input",function(){
	var $tr = $(this).parent().parent()
	calcularPrecioTotalNeto($tr)
	get_total();	
});

function calcularPrecioTotalNeto($tr){
	$precio_unitario = $tr.find("[name*='-precio_unitario']")
	$precio_total_neto = $tr.find("[name*='-precio_total_neto']")
	$unidades = $tr.find("[name*='-unidades']")
	$descuento_porcentaje = $tr.find("[name*='-descuento_porcentaje']")
	if ($descuento_porcentaje.val()=='') {
		$descuento_porcentaje.val('0')
	}
	var precio_total_neto = parseFloat($unidades.val())*parseFloat($precio_unitario.val())
	$precio_total_neto.val((precio_total_neto-(parseFloat($descuento_porcentaje.val())/100*precio_total_neto)).toFixed(2));
}




//Al presionar F8 en la caja de texto de articulo se despliega el modal para ver existencias
$("[name*='-articulo-autocomplete']").on("keydown",function(e){
	if (e.keyCode == 119) {
        	$('#myModal').modal();
        }
});

setInterval(function(){	$(".yourlabs-autocomplete").find("span").attr("style","line-height:30px") }, 1);

$("#buscar-modal").on("click",function(){
	loadArticles()
});



$('#myModal').on('shown.bs.modal', function () {
    $('#modal-clave').focus();
    if (!$("input[name*='-articulo-autocomplete']").last().is(":visible"))
    {
    	$(".btn-success").trigger("click");
    };
});