$(document).ready(function() {
	
	$("#valida_certificados").on("click", valida_certificados);

	function valida_certificados(){
		$.ajax({
			data: {},
			url:'/administrador/valida_datos_facturacion/',
			type : 'get',
			success: function(data){
				if (data.errors.length > 0){
					alert(":/ Error "+ data.errors);
				}
				else{
					if (data.certificados_mal.length>0){
						alert(":/ Los datos de facturacion de ("+data.certificados_mal+") son incorrectos");	
					}
					else
						alert(":) Los datos de facturacion son correctos");
				}	
			},


		});
		

	}
});