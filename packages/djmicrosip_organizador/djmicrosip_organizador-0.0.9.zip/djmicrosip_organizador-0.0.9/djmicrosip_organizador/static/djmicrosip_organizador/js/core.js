$(function () {
    // 6 create an instance when the DOM is ready
    // $('#jstree').jstree();
    // 7 bind to events triggered on the tree
    function cargar_tree($container){

      // $('#jstree').jstree({});
      $container.html("<div></div>");
      var $tree_div = $container.find("div");

      $.ajax({
        url:'/organizador/get_structure/', 
        type : 'get', 
        data:{}, 
        success: function(data){
          $tree_div.jstree({
             "core" : {
               "animation" : 0,
               "check_callback" : true,
               "themes" : { "stripes" : false },
               'data' : data.data,
             },
             
             "plugins" : [ "contextmenu", "dnd", "search", "sort", "state", "types", "unique", "wholerow" ]
           });
        },
        error: function() {
          },
      });
    }

    cargar_tree($("#treeContainer"));
  });



// $("#show_tree").on("click", function(){
//   $contenedor = $("#moverTreeId");
//   loadTree($contenedor);
//   $("#moveTree_ModalId").modal();
// });

// function loadTree($contenedor){
//   $contenedor.html('<div></div>');
//   $contenedor = $contenedor.find('div');
//   $.ajax({
//     url:'/organizador/get_structure/', 
//     type : 'get', 
//     data:{}, 
//     success: function(data){ 
//       $contenedor.jstree({
//         "core" : {
//           "animation" : 0,
//           "check_callback" : true,
//           "themes" : { "stripes" : false },
//           'data' : data,
//         }, 
//         "plugins" : [ "contextmenu", "dnd", "search", "sort", "state", "types", "unique", "wholerow" ]
//       });
//     },
//     error: function() {},
//   });
// }