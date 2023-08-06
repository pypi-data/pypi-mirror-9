$("#crear_txt").on("click",function(){
	var checked_repos = $(".chk_repo:checked");
	var dic_diot = {}
	checked_repos.each(function(){
		var tipo_proveedor = $(this).parent().parent().find("#tipo_proveedor_select").val();
		var actividad_principal = $(this).parent().parent().find("#actividad_principal").val();
		var rfc = $(this).parent().parent().find("#rfc").text();
		var importe = parseFloat($(this).parent().parent().find("#importe").text().replace("$ ",""));
		var iva = parseFloat($(this).parent().parent().find("#iva").text().replace("$ ",""));
		var folio = parseFloat($(this).parent().parent().find("#folio").text());
		if (rfc in dic_diot == false){
			dic_diot[rfc] = {}
			dic_diot[rfc]['importe'] = 0
			dic_diot[rfc]['iva'] = 0
			dic_diot[rfc]['detalles'] = []
		}
		dic_diot[rfc]['tipo_proveedor'] = tipo_proveedor;
		dic_diot[rfc]['actividad_principal'] = actividad_principal;
		dic_diot[rfc]['importe'] += importe;
		dic_diot[rfc]['iva'] += iva;
		// dic_diot[rfc]['detalles'].append((folio,importe))
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
		complete:function(data){
		}
	})
});