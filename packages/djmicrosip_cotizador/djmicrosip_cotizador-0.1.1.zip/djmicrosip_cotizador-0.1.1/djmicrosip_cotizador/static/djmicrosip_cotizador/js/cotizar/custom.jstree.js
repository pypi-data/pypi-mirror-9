var selected_node = 1;

function loadNodeTree(node_id, $contenedor){
	// Cargar arbol de nodos
	$.ajax({
		url:'/cotizador/get_node_structure/', 
		type : 'get', 
		data:{
			'node_id':node_id,
		}, 
		success: function(data){ 
			var data = data.data;
			$contenedor.html("<div></div>");
			$contenedor_div = $contenedor.find("div");

			$contenedor_div.jstree({
			   "core" : {
			     "animation" : 0,
			     "check_callback" : true,
			     "themes" : { "stripes" : false },
			     'data' : data,
			   },
			   
			   "plugins" : [ "contextmenu", "dnd", "search", "sort", "state", "types", "unique", "wholerow" ]
			 });

			$contenedor_div.on('select_node.jstree', function (e, data) {
				$("#selectedFolderId").val(data.node.id)
		    	loadArticles()
			});
		},
		error: function() {
			alert("fallo");
	  	},
	});
}

function loadArticles(){
	var folder_id = $("#selectedFolderId").val()
	lista_precios_id = $("#select_lista_precios").val()
	var moneda_id = $("#select_monedas").val()
	var tipo_cambio = $('#id_tipo_cambio_d').val()
	var articulo_busqueda = $("#id_modal_nombre").val()
	$.ajax({
 	   	url:'/cotizador/cotizar/articulos_search/',
 	   	type : 'get',
 	   	data : {
 	   		'lista_precios_id':lista_precios_id,
 	   		'articulo_busqueda':articulo_busqueda,
 	   		'folder_id':folder_id,
 	   		'moneda_id': moneda_id,
 	   		'tipo_cambio': tipo_cambio,
 	   	},
 	   	success: function(data){
 	   		if (data.articulos.length > 0)
 	   		{
 	   			
	 	   		$('#articles_table2').find('tbody').html('')

	 	   		data.articulos.forEach(function(articulo) {
					$('#articles_table2').find('tbody').append( "<tr> <td> "+articulo.clave+" </td> <td id='nombre'>"+  articulo.nombre+"</td> <td>"+articulo.existencia+"</td><td>"+parseFloat(articulo.precio).toFixed(2)+" </td><td> <button class='btn btn-default add'><i class='glyphicon glyphicon-plus'></i><input type='hidden' value='"+articulo.id+"'> </a> </td> </tr>" );	
				});

				
				$(".add").on("click",function(){
					var articulo_id = $(this).find("input").val()
					var articulo_nombre = $(this).parent().parent().find("#nombre").text()
					loadArticle($articulo,articulo_id,articulo_nombre)
					$("#modal_arbol").modal("hide")
					$('#articles_table2').find('tbody').html('')
					$("#modal-clave").val("")
					$("#modal-nombre").val("")
					$(this).parent().parent().find("input[name*='-precio_unitario']").focus()

				});
 	   		}
 	   		else
 	   		{
 	   			$('#articles_table2').find('tbody').html('No hay articulos')
 	   		};
 	   		$("#buscar-modal").attr("disabled",false)
 	   	},
	});
}