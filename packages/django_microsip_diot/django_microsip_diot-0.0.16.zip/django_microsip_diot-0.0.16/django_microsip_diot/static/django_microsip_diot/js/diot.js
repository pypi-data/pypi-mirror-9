var page = 1;


$("#integrar").on("change",function(){
	var checked = $(this).is(":checked");
	$(".chk_repo").each(function(){
		$(this).attr("checked",checked);
	});
});

$("#sincronizar_catalogo").on("click",function(){
	$("#sincronizar_catalogo").attr("disabled",true);
	$.ajax({
		url:'/diot/exporta_proveedores',
		type:'get',
		data:{
		},
		success:function(data){
			if (data.nuevos > 0)
			{
				alert("se agregaron "+data.nuevos+" Proveedores nuevos.");
			}
			else
			{
				alert("Proceso Terminado.\nNo se agregaron nuevos proveedores.");
			};
			$("#sincronizar_catalogo").attr("disabled",false);
		},
		error:function(data){
			$("#sincronizar_catalogo").attr("disabled",false);
			alert("Error Interno en el servidor");
		}
	})
});

$("#crear_txt").on("click",function(){
	var checked_repos = $(".chk_repo:checked");
	var dic_diot = {}
	checked_repos.each(function(){
		var tipo_proveedor = $(this).parent().parent().find("#tipo_proveedor_select").val();
		var actividad_principal = $(this).parent().parent().find("#actividad_principal").val();
		var rfc = $(this).parent().parent().find("#rfc").text();
		var importe = parseFloat($(this).parent().parent().find("#importe").text().replace("$ ",""));
		var iva = parseFloat($(this).parent().parent().find("#iva").text().replace("$ ",""));
		var folio = $(this).parent().parent().find("#folio").text().trim();
		var tasa0 = 0;
		var tasa16 = (iva *116/16);
		if ((importe-tasa16)>2)
		{
			tasa0=importe-tasa16;
		}
		else if (tasa16>importe)
		{
			tasa0=0;
		};

		if (rfc in dic_diot == false){
			dic_diot[rfc] = {}
			dic_diot[rfc]['tasa0'] = 0
			dic_diot[rfc]['tasa16'] = 0
			dic_diot[rfc]['detalles'] = []
		}
		dic_diot[rfc]['tipo_proveedor'] = tipo_proveedor;
		dic_diot[rfc]['actividad_principal'] = actividad_principal;
		dic_diot[rfc]['tasa0'] += tasa0;
		dic_diot[rfc]['tasa16'] += tasa16;
		dic_diot[rfc]['detalles'].push([String(folio),importe,iva])
	});
	$.ajax({
		url:'/diot/create_file',
		type:'get',
		data:{
			'dic_diot':JSON.stringify(dic_diot),
		},
		success:function(data){
			window.location.replace(this.url);
		},
		error:function(data){
			alert("Error");
		}
	})
});

$(window).scroll(function() {
   if($(window).scrollTop() + $(window).height() == $(document).height()) {
       page+=1;
       $.ajax({
      		url:'/diot/paginacion',
      		type:'get',
      		data:{
      			'page':page,
      			'fecha_inicio':fecha_inicio,
      			'fecha_fin':fecha_fin,
      		},
      		success:function(data){
      			if (!data.error)
      			{
      				data.pagina.forEach(function(repo){
      					$('#tabla_repositorios').find('tbody').append( "<tr> <td> <input type='checkbox' class='chk_repo' value='"+repo[0].id+"' checked='checked'>  </td> <td id='folio'> "+  repo[0].folio+"</td> <td id='nombre'>"+repo[0].nombre+"</td><td id='rfc'>"+repo[0].rfc+"</td><td id='importe'>$ "+repo[0].importe+"</td> <td id='iva'>$ "+repo[1]+"</td></tr>" );
      				});
      			}
      			
      		},
      		error:function(data){
      		}
       });

   }
});