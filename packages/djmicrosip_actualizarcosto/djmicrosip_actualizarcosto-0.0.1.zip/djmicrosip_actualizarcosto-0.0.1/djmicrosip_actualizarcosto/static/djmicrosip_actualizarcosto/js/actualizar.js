// Funcion que carga el articulo seleccionado en autocomplete
function cargar_articulo($articulo, articulo_id, articulo_nombre){ 
	$articulo.parent().find(".deck.div").attr('style','');
	$articulo.parent().find(".deck.div").html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
	$articulo.parent().parent().find("select[name*='-articulo']").html('<option selected="selected" value="'+articulo_id+'"></option>');
	$articulo.parent().find("input").hide();
	$articulo.parent().parent().find("select[name*='-articulo']").trigger( "change" );
	$articulo.parent().show();
	$articulo.parent().parent().show();
}

//AL QUITAR EL FOCO DE LA CLAVE
$("#id_clave").on("focusout",function(){
	var $this = $(this);
	var clave = $this.val();
	if (clave != '')
	{
		$.ajax({
	 	   	url:'/actualizarcosto/articulo_by_clave/',
	 	   	type : 'get',
	 	   	data : {
	 	   		'clave':clave,
	 	   	},
	 	   	success: function(data){
	 	   		if (data.articulo_id == null)
	 	   		{
	 	   			alert("No se encontraron articulos con esta clave");
	 	   			$("#id_clave").focus();
	 	   			$("#id_clave").select();
	 	   		}
	 	   		else
	 	   		{
					$articulo = $this.parent().parent().find("#id_articulo_text");
					cargar_articulo($articulo,data.articulo_id,data.articulo_nombre);
					alert("");
					window.location.replace("/actualizarcosto/articulo/"+data.articulo_id);
	 	   		};
			},
		});
	};
});

// Al Seleccionar el articulo
$("#id_articulo").on("change",function(){
	var articulo_id = $(this).val();
	
	if (articulo_id != null)
	{
		// alert("");
		window.location.replace("/actualizarcosto/articulo/"+articulo_id);
	}
});


