// Variables de valores en cajas de texto
var precio_ultima_compra;
var precioa;
var preciob;
var precioc;
var preciod;
var precioa_iva;
var preciob_iva;
var precioc_iva;
var preciod_iva;
var margena;
var margenb;
var margenc;
var margend;
var $precio_ultima_compra = $("#id_ultima_compra");
var $precioa = $("#id_articuloprecio_set-0-precio");
var $preciob = $("#id_articuloprecio_set-1-precio");
var $precioc = $("#id_articuloprecio_set-2-precio");
var $preciod = $("#id_articuloprecio_set-3-precio");
var $margena = $("#id_articuloprecio_set-0-margen");
var $margenb = $("#id_articuloprecio_set-1-margen");
var $margenc = $("#id_articuloprecio_set-2-margen");
var $margend = $("#id_articuloprecio_set-3-margen");
var $precioa_iva = $("#id_precio_mas_iva1");
var $preciob_iva = $("#id_precio_mas_iva2");
var $precioc_iva = $("#id_precio_mas_iva3");
var $preciod_iva = $("#id_precio_mas_iva4");



$( document ).ready(function() {
	// Se recortan los decimales
	$precio_ultima_compra.focus();
	$precio_ultima_compra.select();
	var precios_text = $("[name*='-precio']");
	precios_text.each( function(){
		var valor = $(this).val();
		valor = parseFloat(valor)
		$(this).val(valor.toFixed(2));
		$(this).attr("size","10");
	});

	var margen_text = $("[name*='-margen']");
	margen_text.each( function(){
		var valor = $(this).val();
		valor = parseFloat(valor)
		$(this).val(valor.toFixed(2));
		$(this).attr("size","8");
	});
	$("#id_ultima_compra").attr("size","10");
	$("#id_ultima_compra").val(parseFloat($("#id_ultima_compra").val()).toFixed(2));
	// Termina de recortar Decimales

	$("#id_iva_container").hide();
	get_valores();
	$precioa_iva.val((parseFloat(precioa)*1.16).toFixed(2));
	$preciob_iva.val((parseFloat(preciob)*1.16).toFixed(2));
	$precioc_iva.val((parseFloat(precioc)*1.16).toFixed(2));
	$preciod_iva.val((parseFloat(preciod)*1.16).toFixed(2));
	get_valores();

});


function get_valores(){
	precio_ultima_compra = parseFloat($("#id_ultima_compra").val());
	precioa = parseFloat($("#id_articuloprecio_set-0-precio").val());
	preciob = parseFloat($("#id_articuloprecio_set-1-precio").val());
	precioc = parseFloat($("#id_articuloprecio_set-2-precio").val());
	preciod = parseFloat($("#id_articuloprecio_set-3-precio").val());
	
	margena = parseFloat($("#id_articuloprecio_set-0-margen").val());
	margenb = parseFloat($("#id_articuloprecio_set-1-margen").val());
	margenc = parseFloat($("#id_articuloprecio_set-2-margen").val());
	margend = parseFloat($("#id_articuloprecio_set-3-margen").val());

	precioa_iva = parseFloat($("#id_precio_mas_iva1").val());
	preciob_iva = parseFloat($("#id_precio_mas_iva2").val());
	precioc_iva = parseFloat($("#id_precio_mas_iva3").val());
	preciod_iva = parseFloat($("#id_precio_mas_iva4").val());
}


function cambia_precio_ultima_compra(){
	get_valores();
	var temporal = ((((precioa/precio_ultima_compra)-1)*100)>0)?(((precioa/precio_ultima_compra)-1)*100):0;
	$margena.val(temporal.toFixed(2));
	temporal = ((((preciob/precio_ultima_compra)-1)*100)>0)?(((preciob/precio_ultima_compra)-1)*100):0;
	$margenb.val(temporal.toFixed(2));;
	temporal = ((((precioc/precio_ultima_compra)-1)*100)>0)?(((precioc/precio_ultima_compra)-1)*100):0;
	$margenc.val(temporal.toFixed(2));
	temporal = ((((preciod/precio_ultima_compra)-1)*100)>0)?(((preciod/precio_ultima_compra)-1)*100):0;
	$margend.val(temporal.toFixed(2));
}

function cambia_precioa(){
	get_valores();	
	var temporal = ((((precioa/precio_ultima_compra)-1)*100)>0)?(((precioa/precio_ultima_compra)-1)*100):0;
	$margena.val(temporal.toFixed(2));
	$precioa_iva.val((temporal*1.16).toFixed(2));
}

function cambia_preciob(){
	get_valores();	
	var temporal = ((((preciob/precio_ultima_compra)-1)*100)>0)?(((preciob/precio_ultima_compra)-1)*100):0;
	$margenb.val(temporal.toFixed(2));
	$preciob_iva.val((temporal*1.16).toFixed(2));
}

function cambia_precioc(){
	get_valores();	
	var temporal = ((((precioc/precio_ultima_compra)-1)*100)>0)?(((precioc/precio_ultima_compra)-1)*100):0;
	$margenc.val(temporal.toFixed(2));
	$precioc_iva.val((temporal*1.16).toFixed(2));
}

function cambia_preciod(){
	get_valores();	
	var temporal = ((((preciod/precio_ultima_compra)-1)*100)>0)?(((preciod/precio_ultima_compra)-1)*100):0;
	$margend.val(temporal.toFixed(2));
	$preciod_iva.val((temporal*1.16).toFixed(2));
}

function cambia_margena(){
	get_valores();	
	var temporal = ((precio_ultima_compra/((margena/100)+1))>0)?((precio_ultima_compra/((margena/100)+1))):0;
	$precioa.val(temporal.toFixed(2));
}

function cambia_margenb(){
	get_valores();	
	var temporal = ((precio_ultima_compra/((margenb/100)+1))>0)?((precio_ultima_compra/((margenb/100)+1))):0;
	$preciob.val(temporal.toFixed(2));
}

function cambia_margenc(){
	get_valores();	
	var temporal = ((precio_ultima_compra/((margenc/100)+1))>0)?((precio_ultima_compra/((margenc/100)+1))):0;
	$precioc.val(temporal.toFixed(2));
}

function cambia_margend(){
	get_valores();	
	var temporal = ((precio_ultima_compra/((margend/100)+1))>0)?((precio_ultima_compra/((margend/100)+1))):0;
	$preciod.val(temporal.toFixed(2));
}

function cambia_ch_iva(){
	if ($(this).is(':checked'))
	{
		$("#id_iva_container").show();
	}
	else
	{
		$("#id_iva_container").hide();
	};
}

function cambia_precioa_mas_iva(){
	get_valores();
	$precioa.val((parseFloat($precioa_iva.val())/1.16).toFixed(2));
	cambia_precioa();
}

function cambia_preciob_mas_iva(){
	get_valores();
	$preciob.val((parseFloat($preciob_iva.val())/1.16).toFixed(2));
	cambia_preciob();
}

function cambia_precioc_mas_iva(){
	get_valores();
	$precioc.val((parseFloat($precioc_iva.val())/1.16).toFixed(2));
	cambia_precioc();
}
function cambia_preciod_mas_iva(){
	get_valores();
	$preciod.val((parseFloat($preciod_iva.val())/1.16).toFixed(2));
	cambia_preciod();
}

$("#id_check_iva").on("change",cambia_ch_iva);
$("#id_ultima_compra").on("input",cambia_precio_ultima_compra);
$precioa.on("input",cambia_precioa);
$preciob.on("input",cambia_preciob);
$precioc.on("input",cambia_precioc);
$preciod.on("input",cambia_preciod);
$margena.on("input",cambia_margena);
$margenb.on("input",cambia_margenb);
$margenc.on("input",cambia_margenc);
$margend.on("input",cambia_margend);

$precioa_iva.on("input",cambia_precioa_mas_iva);
$preciob_iva.on("input",cambia_preciob_mas_iva);
$precioc_iva.on("input",cambia_precioc_mas_iva);
$preciod_iva.on("input",cambia_preciod_mas_iva);