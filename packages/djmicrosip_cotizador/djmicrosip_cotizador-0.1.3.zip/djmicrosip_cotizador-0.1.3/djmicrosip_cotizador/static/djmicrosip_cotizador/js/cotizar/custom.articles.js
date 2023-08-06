function loadArticle($articulo, articulo_id, articulo_nombre){ 
	// Funcion que carga el articulo seleccionado en autocomplete
	$articulo.parent().find(".deck.div").attr('style','');
	$articulo.parent().find(".deck.div").html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
	$articulo.parent().parent().find("select[name*='-articulo']").html('<option selected="selected" value="'+articulo_id+'"></option>');
	$articulo.parent().find("input").hide();
	$articulo.parent().parent().find("select[name*='-articulo']").trigger( "change" );
	$articulo.parent().show();
	$articulo.parent().parent().show();
}

//Para buscar articulos por clave
$("input[name*='-clave']").on("focusout",function(){
	var $this = $(this);
	var clave = $this.val();
	if (clave != '')
	{
		$.ajax({
	 	   	url:'/cotizadorm/articulo_by_clave/',
	 	   	type : 'get',
	 	   	data : {
	 	   		'clave':clave,
	 	   	},
	 	   	success: function(data){
	 	   		if (data.articulo_id == null)
	 	   		{
	 	   			alert("No se encontraron articulos con esta clave");
	 	   			$this.focus();
	 	   		}
	 	   		else
	 	   		{
					$articulo = $this.parent().parent().find("input[name*='-articulo']");
					loadArticle($articulo,data.articulo_id,data.articulo_nombre);
					$this.parent().parent().find("input[name*='-precio_unitario']").focus();
	 	   		};
			},
		});
	};
});

// Al Seleccionar el articulo
$("select[name*='-articulo']").on("change",function(){
	var $articulo = $(this)
	var $articulo_contenedor = $articulo.parent().parent().parent()
	$articulo_contenedor.attr('class','col-md-offset-1 col-lg-11 col-md-11 col-sm-11 col-xs-11 articuloContainer')

	var articulo_id = $articulo.val()

	var $tr = $(this).parent().parent().parent().parent().parent().parent()

	var $precio_unitario = $tr.find("[name*='-precio_unitario']")
	var $precio_total_neto = $tr.find("[name*='-precio_total_neto']")
	var $unidades = $tr.find("[name*='-unidades']")
	var $existencia = $tr.find("[name*='-existencia']")
	var $clave = $tr.find("[name*='-clave']")
	var moneda_id = $("#select_monedas").val()
	var $lista_precios = $("#select_lista_precios")
	// Si se seleciono un articulo
	if (articulo_id != null)
	{
		var tipo_cambio = $('#id_tipo_cambio_d').val()
		$.ajax({
	 	   	url:'/cotizador/cotizar/get_precio/',
	 	   	type : 'get',
	 	   	data : {
	 	   		'articulo_id':articulo_id,
	 	   		'lista_precios_id':$lista_precios.val(),
	 	   		'moneda_id':moneda_id,
	 	   		'tipo_cambio':tipo_cambio,
	 	   	},
	 	   	success: function(data){
	 	   		$precio_unitario.val(parseFloat(data.precio).toFixed(2))
	 	   		$precio_unitario.select()
	 	   		get_total()

	 	   		$clave.parent().hide()
	 	   		$tr.find('.detalle-btnBuscar').parent().hide()
	 	   		$precio_unitario.trigger('input')
	 	   		$(this).parent().parent().attr("class","col-xs-12")
			},
		});
	}
	else
	{
		$precio_total_neto.val(0)
		$precio_unitario.val(0)
		$clave.parent().show()
		$tr.find('.detalle-btnBuscar').parent().show()
   		$articulo_contenedor.attr("class","col-lg-7 col-md-7 col-sm-7 col-xs-7 articuloContainer");
   		$clave.focus();
	};
});

function get_total(){
	var total = 0;
	var subtotal = 0;
	$("[name*='-precio_total_neto']").each(function(){
		if ($(this).val() != '')
		{
			total += parseFloat($(this).val());
			var precio_unitario = parseFloat($(this).parent().parent().find("[name*='-precio_unitario']").val());
			var unidades = parseFloat($(this).parent().parent().find("[name*='-unidades']").val());
			subtotal += unidades*precio_unitario;
		};
		
	});
	var descuento = subtotal - total;
	$total.text(total.toFixed(2));
	$subtotal.text(subtotal.toFixed(2));
	$descuento.text(descuento.toFixed(2));
	if ((subtotal-total)<0.01)
	{
		$(".sub").hide();
		$(".des").hide();
	}
	else
	{
		$(".sub").show();
		$(".des").show();
	};
	if (total=0)
	{
		$(".descuento_tp").hide();
		$(".total_con_descuento").hide();
	};
}