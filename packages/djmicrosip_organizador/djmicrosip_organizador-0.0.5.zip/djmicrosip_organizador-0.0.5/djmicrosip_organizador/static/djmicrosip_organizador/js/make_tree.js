var creado= false;
var selected;
var selected_array =[];
var i;
$("#enviar").on('click',move_articles);

$(document).ready(function(){
	$("input[name='articles_all']").on("click", sellect_all);
	function sellect_all(){
		var to_select = this.checked;
		$("input[type='checkbox'][name='articles']").each(function(){
			this.checked = to_select;
		});
	}
	
	$.ajax({
		url:'/organizador/get_structure/', 
		type : 'get', 
		data:{}, 
		success: function(data){ 

			data=JSON.parse(data);
			cargar_arbol(data);
		},
		error: function() {
	  	},
	});

});

function cargar_arbol(data){
	$('#demo1').jstree({
	   "core" : {
	     "animation" : 0,
	     "check_callback" : true,
	     "themes" : { "stripes" : false },
	     'data' : data,
	   },
	   
	   "plugins" : [ "dnd", "search", "sort", "state", "types", "unique", "wholerow" ]
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
				type : 'get', 
				data:{
					'value':value,
					'selected':selected
				}, 
				success: function(data){ 
					debugger;
				},
				error: function() {
					debugger;
			  	},
			});		
		});
	}
	else{
		alert('Selecciona al menos un articulo');
	};
	


}


$('#demo1')
   // listen for event
   .on('select_node.jstree', function (e, data) {
    	selected=data.node.id;
   })