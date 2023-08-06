var contador = 1
var total = 0

$('#actualizar_btn').on('click', function(){
	var sysdba_password = $('#id_sysdba_password').val()
	$.ajax({
	   	url:'/djmicrosip_utilerias/get_articulos_ids/',
	   	type : 'get',
	   	data : {
	   		'sysdba_password':sysdba_password,
	   	},
	   	success: function(data){

	   		if (data.error == null){
	   			$("#progress").show()
	   			var array_ids = data.articulos_ids.chunk(60);
	   			total = array_ids.length
	   			array_ids.forEach(function(sub_ids){
					actualizar_margenes(sub_ids.join(','))
				});
	   		}
	   		else{
				alert(data.error)
	   		}
		},
	});
});


Array.prototype.chunk = function ( n ) {
    if ( !this.length ) {
        return [];
    }
    return [ this.slice( 0, n ) ].concat( this.slice(n).chunk(n) );
};

function actualizar_margenes(articulos_ids){
	$.ajax({
	   	url:'/djmicrosip_utilerias/actualiza_margenes_ajax/',
	   	type : 'get',
	   	data : {
	   		'articulos_ids':articulos_ids,
	   	},
	   	complete: function(data){
	   		actualizar_progress()
		},
	});
}

function actualizar_progress(){
	var porcentaje = (contador / total * 100).toFixed(2);
	$("#progress").find("div").attr("style","width:"+porcentaje+"%");
	$("#progress").find("div").text(porcentaje+"%");
	if (porcentaje >= 100)
	{
		alert("Proceso Terminado");
		location.reload();
	}
	contador = contador + 1;
}