// function cargar_hijos(){
// 	var parent_id = $(this).val();
// 	$.ajax({
// 		url:'/cotizador/get_folder_children/',
// 		type:'get',
// 		data:{
// 			'parent_id':parent_id,
// 		},
// 		success:function(data){
// 			$("select[name*='-carpeta']").each(function(){
// 				var $select = $(this);
// 				$select.html('');
// 				var children = data.children;
// 				children.forEach(function(item){
// 					$select.append("<option value="+item[0]+">"+item[1]+"</option>");
// 				});
// 			});
// 		},
// 		complete:function(data){

// 		},
// 	});
	
// }

function agregar(){
	$("#id_carpeta_base").trigger("change");
}

// $("#id_carpeta_base").on("change",cargar_hijos);