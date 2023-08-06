var page = 1;
var id_selected=0;

var $tasa_iva_modal = $("#tasa_iva_modal");
var $importe_sin_iva_modal = $("#importe_sin_iva_modal");
var $proporcion_modal = $("#proporcion_modal");
var $iva_acreditable_modal = $("#iva_acreditable_modal");
var $iva_sin_acreditar_modal = $("#iva_sin_acreditar_modal");
var $iva_retenido_modal = $("#iva_retenido_modal");
var $id_xml = $("#id_xml");

// $(document).bind("contextmenu",function(e){
//     return false;
// });

$("#integrar").on("change",function(){
	var checked = $(this).is(":checked");
	$(".chk_repo:enabled").each(function(){

		$(this).attr("checked",checked);
		$(this).trigger("change");
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
		var pagado = parseFloat($(this).parent().parent().find("#pagado").text().replace("$ ",""));
		var pagado_h = parseFloat($(this).parent().parent().find("#pagado_h").val());
		var extranjero = 'N'
		debugger;
		if (rfc == "None")
		{
			rfc=id_fiscal;
			extranjero = 'S'
		}
		var tasa0 = 0;
		var tasa16 = 0;

		if (descuento>0)
		{
			if ($(this).parent().parent().attr("style") != "background-color: bisque;")
			{
				importe = subtotal-descuento;
			}
			else
			{
				if (iva == 0)
				{
					importe = pagado-pagado_h;
				}
				else
				{
					importe = pagado-(pagado_h/1.16);
				};
			};

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

	checked_repos.each(function(){
		var integrar = 'N';
		var id = $(this).val();
		var row = $(this).parent().parent();	
		if (row.attr("style") != "background-color: bisque;")
		{

			$.ajax({
				url:'/diot/pago_total',
				type:'get',
				data:{
					'id': id,
				},
				success:function(data){
				},
				error:function(data){
				}
			});
		}
		else
		{
			var pago = parseFloat($(this).parent().parent().find("#pagado").text().replace("$ ",""));
			$.ajax({
				url:'/diot/pago_parcial',
				type:'get',
				data:{
					'id': id,
					'pago':pago,
				},
				success:function(data){
				},
				error:function(data){
				}
			});
		};				
	});


	$.ajax({
		url:'/diot/create_file',
		type:'get',
		data:{
			'dic_diot':JSON.stringify(dic_diot),
			'fecha_inicio':fecha_inicio,
			'detallado':detallado,
		},
		success:function(data){
			
		},
		error:function(data){
			alert("Error.\nSe recomienda Sincronizar el Catalogo de Proveedores antes de generar el archivo.");
		},
		complete:function(){
			window.location.replace(this.url);

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
      			'repos_ext':repos_ext,
      		},
      		success:function(data){
      			if (!data.error)
      			{
					
      				data.pagina.forEach(function(repo){

      					var options = { year: "numeric", month: "long",
      						day: "numeric" };
      					var style = "";
      					var fecha = new Date(repo[0].fecha);
      					var fecha_ini = new Date(fecha_inicio);
      					fecha_string = fecha.toLocaleDateString("es-es",options);
      					debugger;
      					if (fecha<fecha_ini)
      					{
      						style = "style='background-color: rgb(255, 105, 105);'";
      					};

      					$('#tabla_repositorios').find('tbody').append( "<tr> <td> <input type='checkbox' class='chk_repo' value='"+repo[0].id+"'>  </td><td id='fecha' "+style+"><small>"+fecha_string+"</small></td> <td id='folio'> "+  repo[0].folio+"<input type='hidden' id='tipo_comprobante' value='"+repo[0].tipo_comprobante+"''></td> <td id='nombre'><small>"+repo[0].nombre+"</small><input type='hidden' id='pagado_h' value='"+repo[0].pagado+"}}'><input type='hidden' id='pago' value='0'></td><td id='rfc'>"+repo[0].rfc+" <input type='hidden' id='id_fiscal' value='"+repo[0].taxid+"'></td><td id='pagado' class='text-right'>$ "+repo[0].pagado+"</td><td id='importe' class='text-right'>$ "+repo[0].importe+"</td> <td id='iva' class='text-right'>$ "+repo[1]+"<input type='hidden' id='subtotal' value='"+repo[2]+"'>  <input type='hidden' id='descuento' value='"+repo[3]+"'> <input type='hidden' id='iva_retenido' value='"+repo[4]+"'></td><td><button class='btn options' data-toggle='modal' data-target='#options_Modal' ><i class='glyphicon glyphicon-usd'></i></button></td></tr>" );
      					if (repo[0].integrar == 'S')
      					{
      						var $row = $('#tabla_repositorios').find('tbody').find("tr").last();
      						if (parseFloat(repo[0].pagado < repo[0].importe))
      						{
      							$row.attr("style","background-color: bisque;");
      						};
      					};
      					
      				});
      				var num_mostrados = String($("#tabla_repositorios").find("tr").length-1);
      				var total = data.total;
      				$("#paginacion").children().text('Mostrando '+num_mostrados+' de '+String(total))
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

$(".options").on("click",function(){
	$id_xml = $(this).parent().parent().find(".chk_repo");
	var importe = parseFloat($(this).parent().parent().find("#importe").text().replace("$ ",""));
	var iva = parseFloat($(this).parent().parent().find("#iva").text().replace("$ ",""));
	var iva_retenido = parseFloat($(this).parent().parent().find("#iva_retenido").val());
	var descuento = parseFloat($(this).parent().parent().find("#descuento").val());
	var pagado = parseFloat($(this).parent().parent().find("#pagado").text().replace("$ ",""));
	var subtotal = parseFloat($(this).parent().parent().find("#subtotal").val());
	var pagado_h = parseFloat($(this).parent().parent().find("#pagado_h").val());
	var importe_sin_iva;


	if (descuento>0)
		{
			debugger;
			if ($(this).parent().parent().attr("style") != "background-color: bisque;")
			{
				importe = subtotal-descuento;
			}
			else
			{
				if (iva == 0)
				{
					importe = importe-pagado_h;
				}
				else
				{
					importe = importe-(pagado_h/1.16);
				};
			};

		};

	if (subtotal>importe)
	{
		subtotal=importe;
	};

	if (iva==0)
	{
		importe_sin_iva = ((importe ))
		$tasa_iva_modal.val(0);
		$proporcion_modal.attr("disabled",true);
		$iva_acreditable_modal.attr("disabled",true);
		$iva_sin_acreditar_modal.attr("disabled",true);
		$iva_retenido_modal.attr("disabled",true);
	}
	else
	{
		importe_sin_iva = ((importe - pagado)/1.16)
		$tasa_iva_modal.val(16);
		$proporcion_modal.attr("disabled",false);
		$iva_acreditable_modal.attr("disabled",false);
		$iva_sin_acreditar_modal.attr("disabled",false);
		$iva_retenido_modal.attr("disabled",false);
	};
	$importe_sin_iva_modal.val(parseFloat(importe_sin_iva.toFixed(2)));
	$proporcion_modal.val(1.0);
	var iva_acreditable = ($importe_sin_iva_modal.val()*$proporcion_modal.val()*$tasa_iva_modal.val()/100).toFixed(2);
	$iva_acreditable_modal.val(iva_acreditable);
	$iva_sin_acreditar_modal.val(0);
	$iva_retenido_modal.val(iva_retenido);
	// $descuento_modal.val(descuento);

});

$("#tasa_iva_modal").on("change",function(){
	if ($("#tasa_iva_modal").val()==0)
	{
		
		$proporcion_modal.attr("disabled",true);
		$iva_acreditable_modal.attr("disabled",true);
		$iva_sin_acreditar_modal.attr("disabled",true);
		$iva_retenido_modal.attr("disabled",true);
	}
	else
	{
		
		$proporcion_modal.attr("disabled",false);
		$iva_acreditable_modal.attr("disabled",false);
		$iva_sin_acreditar_modal.attr("disabled",false);
		$iva_retenido_modal.attr("disabled",false);
	};
});

$("#proporcion_modal").on("input",function(){
	$iva_acreditable_modal.val($importe_sin_iva_modal.val()*$proporcion_modal.val()*$tasa_iva_modal.val()/100);
	$iva_sin_acreditar_modal.val($importe_sin_iva_modal.val()*(1-$proporcion_modal.val())*$tasa_iva_modal.val()/100);
});

$("#importe_sin_iva_modal").on("input",function(){
	$proporcion_modal.trigger("input");
});

$("#modificar_xml").on("click",function(){
	var pagado = parseFloat($id_xml.parent().parent().find("#pagado").text().replace("$ ",""));
	var pagado_final;
	var $row = $id_xml.parent().parent();
	$row.attr("style","background-color: bisque;");
	$('.tags-modal-md').modal('hide');
	$row.find(".chk_repo").attr("checked","checked");
	$row.find(".chk_repo").attr("disabled",false);
	if ($(tasa_iva_modal).val()!=0)
	{
		var importe_mas_iva = parseFloat(($importe_sin_iva_modal.val() * (1+($tasa_iva_modal.val()/100))).toFixed(2));
		pagado_final = importe_mas_iva+pagado;
		$row.find("#subtotal").val(parseFloat($importe_sin_iva_modal.val()));
	}
	else
	{	
		pagado_final = parseFloat($importe_sin_iva_modal.val())+pagado;
		$row.find("#subtotal").val(parseFloat($importe_sin_iva_modal.val()));
	}
	
	$row.find("#pagado").text("$ "+pagado_final)
});

$(".chk_repo").on("change",function(){

	var row = $(this).parent().parent();
	if ((row.attr("style") == "background-color: bisque;") && (!$(this).is(":checked")) )
	{
		$(this).attr("disabled",true);
		var pagado_inicial = row.find("#pagado_h").val()
		row.find("#pagado").text("$ "+pagado_inicial);
	}
	
	var integrar = 'S';
	var id = $(this).val();
	if (!$(this).is(":checked"))
	{
		integrar = 'N'
	};
	$.ajax({
		url:'/diot/change_xml_status',
		type:'get',
		data:{
			'integrar':integrar,
			'id': id,
		},
		success:function(data){
		},
		error:function(data){
		}
	})
});