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
		var rfc = $(this).parent().parent().find("#rfc").text().trim();
		var nombre = $(this).parent().parent().find("#nombre").text();
		var id_fiscal = $(this).parent().parent().find("#id_fiscal").val();
		var importe = parseFloat($(this).parent().parent().find("#importe").text().replace("$ ",""));
		var iva = parseFloat($(this).parent().parent().find("#iva").text().replace("$ ",""));
		var iva_retenido = parseFloat($(this).parent().parent().find("#iva_retenido").val());
		var descuento = parseFloat($(this).parent().parent().find("#descuento").val());
		var subtotal = parseFloat($(this).parent().parent().find("#subtotal").val());
		var folio = $(this).parent().parent().find("#folio").text().trim();
		var tipo_comprobante = $(this).parent().parent().find("#tipo_comprobante").val();
		var extranjero = 'N'
		if (rfc == "None")
		{
			rfc=id_fiscal;
			extranjero = 'S'
		}
		// debugger;
		var tasa0 = 0;
		var tasa16 = 0;

		if (descuento>0)
		{
			importe = subtotal-descuento;
		};

		if (subtotal>importe)
		{
			subtotal=importe;
		};


		if (iva == 0)
		{

			tasa0 = subtotal;
		}
		else
		{
			tasa16 = subtotal;
		};
		if (rfc in dic_diot == false){
			dic_diot[rfc] = {}
			dic_diot[rfc]['extranjero'] = extranjero
			dic_diot[rfc]['nombre'] = nombre
			dic_diot[rfc]['tasa0'] = 0
			dic_diot[rfc]['tasa16'] = 0
			dic_diot[rfc]['retenido'] = 0
			dic_diot[rfc]['detalles'] = []
		}
		
		if (tipo_comprobante=='I')
		{
			dic_diot[rfc]['tasa0'] += tasa0;
			dic_diot[rfc]['tasa16'] += tasa16;
			dic_diot[rfc]['retenido'] += iva_retenido;
		}
		dic_diot[rfc]['detalles'].push([String(folio),importe,iva])
	});
	var detallado=false;
	if (confirm("Desea Agregar los detalles por Proveedor al Archivo?")==true)
	{
		detallado = true;
	};

	$.ajax({
		url:'/diot/create_file',
		type:'get',
		data:{
			'dic_diot':JSON.stringify(dic_diot),
			'fecha_inicio':fecha_inicio,
			'detallado':detallado,
		},
		success:function(data){
			window.location.replace(this.url);
		},
		error:function(data){
			alert("Error.\nSe recomienda Sincronizar el Catalogo de Proveedores antes de generar el archivo.");
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
      					$('#tabla_repositorios').find('tbody').append( "<tr> <td> <input type='checkbox' class='chk_repo' value='"+repo[0].id+"' checked='checked'>  </td> <td id='folio'> "+  repo[0].folio+"<input type='hidden' id='tipo_comprobante' value='"+repo[0].tipo_comprobante+"''></td> <td id='nombre'>"+repo[0].nombre+"</td><td id='rfc'>"+repo[0].rfc+" <input type='hidden' id='id_fiscal' value='"+repo[0].taxid+"'></td><td id='importe'>$ "+repo[0].importe+"</td> <td id='iva'>$ "+repo[1]+"<input type='hidden' id='subtotal' value='"+repo[2]+"'>  <input type='hidden' id='descuento' value='"+repo[3]+"'> <input type='hidden' id='iva_retenido' value='"+repo[4]+"'></td></tr>" );
      				});
      			}
      			
      		},
      		error:function(data){
      		}
       });

   }
});

$("#crear_paises").on("click",function(){
	$("#crear_paises").attr("disabled",true);
	$.ajax({
		url:'/diot/crear_paises',
		type:'get',
		data:{
		},
		success:function(data){
			if (data.nuevos > 0)
			{
				alert("se agregaron "+data.nuevos+" Paises nuevos.");
			}
			else
			{
				alert("Proceso Terminado.\nNo se agregaron nuevos paises.");
			};
			$("#crear_paises").attr("disabled",false);
		},
		error:function(data){
			$("#crear_paises").attr("disabled",false);
			alert("Error Interno en el servidor");
		}
	})
});