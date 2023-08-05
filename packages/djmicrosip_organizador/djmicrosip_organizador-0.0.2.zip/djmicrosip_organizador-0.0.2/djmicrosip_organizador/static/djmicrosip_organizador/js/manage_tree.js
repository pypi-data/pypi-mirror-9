var creado= false;
var selected;
var selected_node;
var selected_array =[];
var i;
var page =0;


$(document).ready(function(){
	$("input[name='articles_all']").on("click", sellect_all);
	function sellect_all(){
		var to_select = this.checked;
		$("input[type='checkbox'][name='articles']").each(function(){
			this.checked = to_select;
		});
	}

	cargar_tree();
	

});

$("#enviar").on('click',move_articles);
$("#articles_all").on("click",sellect_all);

function cargar_tree(){
		$.ajax({
			url:'/organizador/get_structure/', 
			type : 'get', 
			data:{}, 
			success: function(data){ 
				// debugger;
				// data=JSON.parse(data);
				cargar_arbol(data.data);
			},
			error: function() {
		  	},
		});
	}


function cargar_arbol(data){
	$('#demo1').jstree({
	   "core" : {
	     "animation" : 0,
	     "check_callback" : true,
	     "themes" : { "stripes" : false },
	     'data' : data,
	   },
	   
	   "plugins" : [ "contextmenu", "dnd", "search", "sort", "state", "types", "unique", "wholerow" ]
	 });
	$('#demo2').jstree({
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

function next_btn(){
	$('html, body').animate({ scrollTop: $(document).height()}, 150);
	page+=1;
	get_articles();

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
						cargar_tree();
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

$('#demo2').on('select_node.jstree', function (e, data) {
    	selected = data.node.id;
   })

