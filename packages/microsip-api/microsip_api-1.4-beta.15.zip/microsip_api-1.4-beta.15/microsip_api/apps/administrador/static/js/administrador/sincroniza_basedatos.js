$(document).ready(function() {
	
	$("#sincroniza_basedatos_link").on("click", sincroniza_basedatos);

	function sincroniza_basedatos(){
		$.ajax({
			data: {},
			url:'/administrador/sincronizar_basedatos/',
			type : 'get',
			success: function(data){
				if (data.errors.length > 0){
					alert(":/ Error "+ data.errors);
				}
				else
					alert(":) Base de datos sincronizada");
			},

		});
		

	}
});