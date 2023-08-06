$("#btn_inicializar").on("click",function(){
	$("#btn_inicializar").attr("disabled",true);
	if (confirm("Seguro que desea Inicializar los pagos de este mes?") == true)
	{
		$.ajax({
			url:'/diot/inicializa_pagos',
			type:'get',
			data:{
				'mes':$("#mes").val(),
				'anio':$("#anio").val(),
			},
			success:function(data){
				alert("Proceso Completado");
				$("#btn_inicializar").attr("disabled",true);
			},
			error:function(data){
				alert("Error Interno en el servidor");
			}
		})
	};	
});