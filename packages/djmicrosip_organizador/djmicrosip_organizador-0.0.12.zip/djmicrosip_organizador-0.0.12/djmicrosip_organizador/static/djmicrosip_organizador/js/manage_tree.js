var creado= false;
var selected;
var selected_node;
var selected_array =[];
var i;
var page =0;



Array.prototype.chunk = function ( n ) {
    if ( !this.length ) {
        return [];
    }
    return [ this.slice( 0, n ) ].concat( this.slice(n).chunk(n) );
};

$(document).ready(function(){
	$("#progress").hide();
	$("input[name='articles_all']").on("click", sellect_all);
	function sellect_all(){
		var to_select = this.checked;
		$("input[type='checkbox'][name='articles']").each(function(){
			this.checked = to_select;
		});
	}

	cargar_tree(0);
});

$("#enviar").on('click',move_articles);
$("#articles_all").on("click",sellect_all);

function cargar_tree(create){
	var contador = 1;
	$.ajax({
		url:'/organizador/get_structure/', 
		type : 'get', 
		data:{}, 
		success: function(data){
			var ids = data.ids;
			var tam = 120;
			var array_ids = ids.chunk(tam);
			// debugger;
			if (ids.length > 0 )
			{
				$("#progress").show();
				array_ids.forEach(function(ids_temp){
					$.ajax({
						url:'/organizador/set_article_in_folder/',
						type:'get',
						data:{
							'articulos_ids':ids_temp.join(','),
						},
						success: function(data){
							
						},
						complete: function(){
							var porcentaje = (contador / array_ids.length * 100).toFixed(2);
							$("#progress").find("div").attr("style","width:"+porcentaje+"%");
							$("#progress").find("div").text(porcentaje+"%");
							if (porcentaje >= 100)
							{
								alert("Proceso Terminado");
								location.reload();
							};
							contador = contador + 1;
						}
					});
				});
				
			};
			cargar_arbol(data.data,$("#demo1"));
			if (create == 1)
			{
				$parent = $("#demo2").parent();
				$parent.html('');
				$parent.html("<div id='demo2'></div>");
				cargar_arbol(data.data,$("#demo2"));
				$parent.append("<br><button type='button' class='btn btn-default' data-dismiss='modal'>Cancelar</button><a href='#' class='btn btn-default' id='enviar' data-dismiss='modal'>Mover</a>");
				$("#enviar").on('click',move_articles);
				$('#demo2').on('select_node.jstree', function (e, data) {
				    selected = data.node.id;
				 });
			}
			else
			{
				cargar_arbol(data.data,$("#demo2"));
			};
			
		},
		error: function() {
	  	},
	});
}


function cargar_arbol(data, $contenedor){
	$contenedor.jstree({
	   "core" : {
	     "animation" : 0,
	     "check_callback" : true,
	     "themes" : { "stripes" : false },
	     'data' : data,
	   },
	   
	   "plugins" : [ "contextmenu", "dnd", "search", "sort", "state", "types", "unique", "wholerow" ]
	 });
}

function sellect_all(){
	seleccionar = this.checked;

	$("input[type='checkbox'][name='articles']").each(function(){
		this.checked = seleccionar;
	});
}
	
function move_articles(){
	$('input:checked').each(function() {
       selected_array.push($(this).val());
     });
	i = selected_array.indexOf("x");
	if(i != -1) {
		selected_array.splice(i, 1);
	}
	if (selected_array.length > 0) {
		$.each(selected_array, function(index, value){

			$.ajax({
				url:'/organizador/move_articles/', 
				type : 'GET', 
				data:{ 'value':value, 'selected':selected }, 
				success: function(data){ 
				},
				error: function() {
			  	},
			});		
		});
	}
	else{
		alert('Selecciona al menos un articulo');
	};
	location.reload(true);
	
}

// function next_btn(){
	
// 	$('html, body').animate({ scrollTop: $(document).height()}, 150);

// }

function get_articles(){
	$.ajax({
		url:'/organizador/get_articles_in_folder/', 
		type : 'get', 
		data:{
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

$('#demo1').on('select_node.jstree', function (e, data) {
    	selected_node = data.node.id;
    	$("#next").remove();
    	page = 1;
    	get_articles();
   })

$('#demo1').on('move_node.jstree', function (e, data) {
    	$.ajax({
    		url:'/organizador/move_folder/', 
    		type : 'get', 
    		data:{ 'folder_id':data.node.id,
    				'parent_id':data.parent, }, 
    		success: function(datajx){ 
    			
    		},
    		error: function() {
    	  	},
    	});
   })

$('#demo1').on('create_node.jstree', function (e, data) {
    	console.log(data.node.parent);
    	creado = true;
   })

$('#demo1').on('delete_node.jstree', function (e, data) {
	$.ajax({
		url:'/organizador/remove_folder/', 
		type : 'get', 
		data:{ 'folder_id':data.node.id, }, 
		success: function(datajx){ 
			if (datajx.remove != 1) {
				data.instance.refresh();
				alert('La carpeta contiene objectos. No se pudo eliminar');
			}
			else
			{
				cargar_tree(1);
			};
		},
		error: function() {
	  	},
	});    	
})

$('#demo1').on('rename_node.jstree', function (e, data) {
	if (creado) {
		var folder;
		$.ajax({
			url:'/organizador/get_folder_id/', 
			type : 'GET', 
			data:{ }, 
			success: function(datajx){ 
				folder_id = datajx.folder_id;
				data.instance.set_id(data.node,folder_id);
				folder_name = data.text;
				parent_id = data.node.parent;
				$.ajax({
					url:'/organizador/create_folder/', 
					type : 'GET', 
					data:{ 'folder_id':folder_id,
							'folder_name':folder_name,
							'parent_id':parent_id, 
					}, 
					success: function(datajx2){ 
						cargar_tree(1);
					},
				}); 	
			},
		});	
		
		
    	creado = false;
	}
	else{
		$.ajax({
			url:'/organizador/rename_folder/', 
			type : 'GET', 
			data:{ 'folder_id':data.node.id,
					'folder_name':data.text,
			}, 
			success: function(datajx2){ 
				
			},
		});
	};
	

   })

$("#show_tree").on("click",function(){
	cargar_tree(1);
});