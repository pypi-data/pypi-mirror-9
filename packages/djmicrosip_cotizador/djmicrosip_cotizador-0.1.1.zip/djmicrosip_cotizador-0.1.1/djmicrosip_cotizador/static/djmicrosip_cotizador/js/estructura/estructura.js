var $Selectedfolder = null
var selected_node =  null
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
			   "selected_node": node_id,
			   "plugins" : [ "contextmenu", "dnd", "search", "sort", "state", "types", "unique", "wholerow" ]
			 });

			$contenedor_div.on('select_node.jstree', function (e, data) {
				$("#selectedFolderId").val(data.node.id)
				$Selectedfolder = $Selectedfolder
				selected_node = data.node.id
			});
		},
		error: function() {
			alert("fallo");
	  	},
	});
}

$("#id_selectFolderBtn").on("click", function(){
	var $fullPathLabel =  $Selectedfolder.parent().find(".folderFullPath");
	$Selectedfolder.val(selected_node);
	getfullpath(selected_node, $("#id_carpeta_base").val(), $fullPathLabel);
	$("#modal_arbol").modal("hide");
});

$('.deleteSelecction').on('click', function(){
	$Selectedfolder = $(this).parent().parent().find("select")
	var selected_node = $Selectedfolder.val()

	$objectToSelect = $(this)
	loadNodeTree($("#id_carpeta_base").val(), $("#id_tree_container"))
	$("#modal_arbol").modal()
});

$('.deleteSelecction').each(function(){
	var selected_node = $(this).parent().parent().find("select").val()
	var $fullPathLabel =  $(this).find(".folderFullPath")
	if (selected_node != '') {
		getfullpath(selected_node, $("#id_carpeta_base").val(), $fullPathLabel)
	}
	else{
		$fullPathLabel.text('Selecciona una carpeta')
	}
})

function getfullpath(child_id, root_id, $fullPathLabel){

	$.ajax({
 	   	url:'/cotizador/get_folderfullpath/',
 	   	type : 'get',
 	   	data : {
 	   		'root_id':root_id,
 	   		'child_id':child_id,
 	   	},
 	   	success: function(data){
 	   		debugger;
 	   		$fullPathLabel.text(data.path)
		},
	});
}

