var selected_node;
var page=1;


$(".selectedArticle").hide();
$("button.close").on("click", function(){
	var tab_id = $(".tab_li.active").find("input").val();
	var tab_nombre = $(".tab_li.active").find("a").text();
	$("#"+tab_nombre).find(".selectedArticle").hide();
	$('#cotizacion_detalle_'+tab_id).find(".cotizacionArticulo-nombre").html("<span class='text-danger'> Sin seleccionar</span>");
	$('#cotizacion_detalle_'+tab_id).find(".cotizacionDetalle-precio").text("");
});

$(".tab_li").on("click",function(){
	var activo = $(".active.tab_li a");
	var div_act = $("#"+activo.parent().text().trim());
	var green = div_act.find(".selectedArticle").is(":visible") ;
	if (green) 
	{
		activo.attr("style","background-color:#b2dba1");
	};
	var current = $(this).find("a").attr("style","");
	// debugger;
})

$(".tab_li").each(function(){

	var nombre = $(this).find("a").text();
	var id = $(this).find("input").val();
	cargar_node_tree(id, $('#tree_'+nombre));
});

function cargar_node_tree(node_id, $contenedor){

	$.ajax({
		url:'/cotizador/get_node_structure/', 
		type : 'get', 
		data:{
			'node_id':node_id,
		}, 
		success: function(data){ 
			cargar_arbol(data.data, $contenedor);
		},
		error: function() {
			alert("fallo");
	  	},
	});
}

function cargar_arbol(data, $contenedor){
	$contenedor.html("<div></div>");
	$contenedor_div = $contenedor.find("div");
	// debugger;
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
    	selected_node = data.node.id;
    	get_articles();
	});
}



function get_articles(){
	$.ajax({
		url:'/organizador/get_articles_in_folder/', 
		type : 'get', 
		data:{
			'selected':selected_node,
			'page':page,
		}, 
		success: function(data){

			var tab_id = $(".tab_li.active").find("input").val();
			var tab_nombre = $(".tab_li.active").find("a").text();
			num_pages = data.pages;
			data = data.data;
			if (page==1) {
				$('#articles_table_'+tab_id).html('<thead><tr><th>Articulo</th><th>Existencia</th><th>Precio</th></tr></thead><tbody><tr></tr></tbody>');
			};			
			data.forEach(function(nombre) {
				$('#articles_table_'+tab_id).find('tbody').append( "<tr> <td>"+  nombre[1]+"</td> <td>"+nombre[3]+"</td><td class='precio'>"+nombre[2]+"</td> </tr>" );
				
			}); 
			if ( page == 1 ) {
				$('#articles_table_'+tab_id).append( '<a href="#" id="next" class="btn btn-default" onClick="next_btn()">Siguiente</a>');

			}
			$("[id*='articles_table']").find("tr").on("click", function(){
				var article = $(this).find("td").first().text();
				var precio_str = $(this).find(".precio").text();
				var precio = parseFloat(precio_str.substring(2, precio_str.length));

				var respuesta = confirm("Selecionar articulo \n"+article);
				if(respuesta){
					// $("#"+tab_nombre).find(".selectArticuleForm").hide();

					$("#"+tab_nombre).find(".selectedArticle").show();
					$("#selected_article_"+tab_id).html(article);
					$('#articles_table_'+tab_id).html('');
					debugger;
					var article_selected = "<span class='deselectArticle'><i class='glyphicon glyphicon-remove text-danger'></i></span>"+article;
					$('#cotizacion_detalle_'+tab_id).find(".cotizacionDetalle-nombre").html(article_selected);

					$('#cotizacion_detalle_'+tab_id).find(".cotizacionDetalle-precio").html('<input class="col-md-10 col-xs-10 col-sm-10 text-right" type="text" value="'+precio+'"/>');
					var total = parseFloat($(".cotizacionTotal input[type='hidden']").val());
					total += precio;

					$(".deselectArticle").on("click", function(){
						var tab_name = $(this).parent().parent().parent().find(".cotizacionDetalle-encabezado>strong").text();
						var $precio =  $(this).parent().parent().find(".cotizacionDetalle-precio");
						precio = parseFloat($precio.text().substring(2,30));
						$(this).parent().parent().find(".cotizacionDetalle-nombre").html('<span class="text-danger">Sin selecionar</span>');
						$precio.html('');
						$('#myTab a[href="#'+ tab_name +'"]').tab('show');
						$('#myTab a[href="#'+ tab_name +'"]').attr("style","");
						$('#'+ tab_name).find('button[class="close"]').click();
						var total = parseFloat($(".cotizacionTotal input[type='hidden']").val());
						total -= precio; 
						total = total.toFixed(2);
						$(".cotizacionTotal input[type='hidden']").val(total);
						$(".cotizacionTotal label").text("$ "+total);
					});
					total = total.toFixed(2);
					$(".cotizacionTotal input[type='hidden']").val(total);
					$(".cotizacionTotal label").text("$ "+total);

				}
			});
			if(page == num_pages){
				$("#next").remove();
			};
			
		},
		error: function() {
			$('#articles_table_'+tab_id).find('tbody').html('');
	  	},
	});
}

