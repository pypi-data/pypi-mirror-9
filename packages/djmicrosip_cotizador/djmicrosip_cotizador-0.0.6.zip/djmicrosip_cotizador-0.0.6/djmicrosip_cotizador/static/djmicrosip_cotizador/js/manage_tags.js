$("#agregar_tag_articulos").on("click", agregar_tag_articulos);

function agregar_tag_articulos(){
	var selected_articles_ids = $('input[name="articles"]:checked').map(function() {return this.value;}).get();
	if ( $("#id_tag").val() != null && selected_articles_ids.length >0){
		$('.tags-modal-sm').modal('hide');
		$.ajax({
			url:'/organizador/agregar_tag_articulo/',
			type : 'get',
			data : {tag_id:parseInt($("#id_tag").val()[0]), articulos_ids: selected_articles_ids.join(",")},

		});
	}
	else if( selected_articles_ids.length === 0 ){
		$('.tags-modal-sm').modal('hide');
		alert("Selecciona al menos un articulo");	
	}
	else{
		alert("Selecciona Un Tag por Favor.");			
	};
}

$("#id_tag_search").on('keydown', function(e) {
	var keyCode = e.keyCode || e.which; 
	if (keyCode == 13) 
	{	
		get_articles_all($("#id_tag_search").val());
		$("#id_tag_search").val('');
	}
});

function get_articles_all(search_text){
	$('#articles_table').find('tbody').html('');
	$("#next").remove();
	$.ajax({
		url:'/organizador/get_articles_in_folder_all/', 
		type : 'get', 
		data:{
			'search_text':search_text,
			'selected':selected_node,
			'page':page,
		}, 
		success: function(data){
			num_pages=data.pages;
			data = data.data;
			if (page==1) {
				$('#articles_table').find('tbody').html('');
			};
			data.forEach(function(nombre) {
				$('#articles_table').find('tbody').append( "<tr> <td> <input type='checkbox' name='articles' value='"+nombre[0]+"'>  </td> <td><a href='/organizador/articulo/"+nombre[0]+"/'> "+  nombre[1]+"</a></td> <td>"+nombre[3]+"</td><td>"+nombre[2]+"</td> </tr>" );
				
			}); 
			if ( page == 1 ) {
				$('#articles_table').append( '<a href="#" id="next" class="btn btn-default" onClick="next_btn()">Siguiente</a>');

			}
			if(page == num_pages){
				$("#next").remove();
			};
			
		},
		error: function() {
			$('#articles_table').find('tbody').html('');
		},
	});
}