var $total = $("#total");
var $subtotal = $("#subtotal");
var $descuento = $("#descuento");
var $descuentop = $("#descuentop");
var $descuento_tp = $("#descuento_tp");
var $total_con_descuento = $("#total_con_descuento");
var moneda_id = $("#select_monedas").val();
var lista_precios_id = $("#select_lista_precios").val();

$(document).ready(function(){
	$(".sub").hide();
	$(".des").hide();
	$(".descuento_tp").hide();
	$(".total_con_descuento").hide();
	$("input[name*='-precio_total_neto']").attr("readonly","true");

});

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

function foco_detalle(){
	$("[name*='-unidades']").last().val(1);
	$("input[name*='-clave']").last().focus();
	$("input[name*='-precio_total_neto']").attr("readonly","true");
	$("[name*='-articulo-autocomplete']").addClass("form-control");
}

function get_total(){
	var total = 0;
	var subtotal = 0;
	$("[name*='-precio_total_neto']").each(function(){
		total += parseFloat($(this).val());
		var precio_unitario = parseFloat($(this).parent().parent().find("[name*='-precio_unitario']").val());
		var unidades = parseFloat($(this).parent().parent().find("[name*='-unidades']").val());
		subtotal += unidades*precio_unitario;

	});
	var descuento = subtotal - total;
	$total.text(total.toFixed(2));
	$subtotal.text(subtotal.toFixed(2));
	$descuento.text(descuento.toFixed(2));
	if (total == subtotal)
	{
		$(".sub").hide();
		$(".des").hide();
	}
	else
	{
		$(".sub").show();
		$(".des").show();
	};
}

$("#descuentop").on("input",function(){
	debugger;
	if ($(this).val() == '') 
	{ 
		$(this).val(0);
		$(this).select();
	};
	var descuentop = parseFloat($("#descuentop").val());
	var subtotal = parseFloat($total.text());
	var descuento_tp = parseFloat(subtotal*descuentop/100);
	var total_con_descuento = parseFloat(subtotal-descuento_tp);
	$total_con_descuento.text(total_con_descuento.toFixed(2));
	$descuento_tp.text(descuento_tp.toFixed(2));

	if (total_con_descuento == subtotal)
	{
		
		$(".descuento_tp").hide();
		$(".total_con_descuento").hide();
	}
	else
	{
		
		$(".descuento_tp").show();
		$(".total_con_descuento").show();
	};

});

$("input").on("keypress", function(e) {
            /* ENTER PRESSED*/
        if (e.keyCode == 13) {
        	$(this).trigger( "focusout" );
        }
    });

//AL QUITAR EL FOCO DE LA CLAVE
$("input[name*='-clave']").on("focusout",function(){
	var $this = $(this);
	var clave = $this.val();
	if (clave != '')
	{
		$.ajax({
	 	   	url:'/cotizadorm/articulo_by_clave/',
	 	   	type : 'get',
	 	   	data : {
	 	   		'clave':clave,
	 	   	},
	 	   	success: function(data){
	 	   		if (data.articulo_id == null)
	 	   		{
	 	   			alert("No se encontraron articulos con esta clave");
	 	   			$this.focus();
	 	   		}
	 	   		else
	 	   		{
					$articulo = $this.parent().parent().find("input[name*='-articulo']");
					cargar_articulo($articulo,data.articulo_id,data.articulo_nombre);
					$this.parent().parent().find("input[name*='-precio_unitario']").focus();
	 	   		};
			},
		});
	};
});

$("input").on("focusin",function(){
	$(this).select();
});

//AL CAMBIAR LA MONEDA A MOSTRAR EN EL SELECT
$("#select_monedas").on("change",function(){	
   		$("#select_monedas").attr("disabled",true);
   		
	   		$("#cotiza").show();
	   		foco_detalle();
	   		$("#id_tipo_cambio_d").attr("disabled",true);
   		
	   	moneda_id = $(this).val();
});

//AL CAMBIAR LA LISTA DE PRECIOS
$("#select_lista_precios").on("change",function(){
		lista_precios_id = $(this).val();	
   		$("select[name*='-articulo']").trigger("change");


});

// Al Seleccionar el articulo
$("select[name*='-articulo']").on("change",function(){
	debugger;
	var articulo_id = $(this).val();
	var select = $(this);
	var $precio_unitario = select.parent().parent().parent().find("[name*='-precio_unitario']");
	var $precio_total_neto = select.parent().parent().parent().find("[name*='-precio_total_neto']");
	var $unidades = select.parent().parent().parent().find("[name*='-unidades']");
	if (articulo_id != null)
	{
		$.ajax({
	 	   	url:'/cotizadorm/get_precio/',
	 	   	type : 'get',
	 	   	data : {
	 	   		'articulo_id':articulo_id,
	 	   		'lista_precios_id':lista_precios_id,
	 	   	},
	 	   	success: function(data){

	 	   		var precio_unitario;
	 	   		var precio_total_neto;
	 	   		var moneda_id = $("#select_monedas").val();
	 	   		var tipo_cambio_d = parseFloat($("#id_tipo_cambio_d").val());
	 	   		if (data.es_moneda_local == 'S')
	 	   		{
	 	   			if (data.moneda_id == moneda_id)
	 	   			{
	 	   				precio_unitario = parseFloat(data.precio).toFixed(2);
	 	   			}
	 	   			else
	 	   			{
	 	   				precio_unitario = (parseFloat(data.precio)/tipo_cambio_d).toFixed(2);	 	   				
	 	   			}; 
	 	   		}
	 	   		else
	 	   		{
	 	   			if (data.moneda_id == moneda_id)
	 	   			{
	 	   				precio_unitario = parseFloat(data.precio).toFixed(2);
	 	   			}
	 	   			else
	 	   			{
	 	   				precio_unitario = (tipo_cambio_d*parseFloat(data.precio)).toFixed(2);
	 	   			}; 
	 	   		};
	 	   		precio_total_neto = (parseFloat($unidades.val())*parseFloat(precio_unitario)).toFixed(2);   		
	 	   		$precio_unitario.val(precio_unitario);
	 	   		$precio_total_neto.val(precio_total_neto);
	 	   		$precio_unitario.select();
	 	   		get_total();
			},
		});
	}
	else
	{
		$unidades.val(1);
		$precio_total_neto.val(0);
		$precio_unitario.val(0);
	};
});

// INPUTS
$("[name*='-precio_unitario']").on("input",function(){
	var select = $(this);
	var $precio_total_neto = select.parent().parent().find("[name*='-precio_total_neto']");
	var $unidades = select.parent().parent().find("[name*='-unidades']");
	$precio_total_neto.val((parseFloat($unidades.val())*(parseFloat(select.val()))).toFixed(2));
	get_total();	
});

$("[name*='-unidades']").on("input",function(){
	var select = $(this);
	var $precio_unitario = select.parent().parent().find("[name*='-precio_unitario']");
	var $precio_total_neto = select.parent().parent().find("[name*='-precio_total_neto']");
	$precio_total_neto.val((parseFloat(select.val())*(parseFloat($precio_unitario.val()))).toFixed(2));
	get_total();
});

$("[name*='-descuento']").on("input",function(){
	var select = $(this);
	var $precio_unitario = select.parent().parent().find("[name*='-precio_unitario']");
	var $precio_total_neto = select.parent().parent().find("[name*='-precio_total_neto']");
	var $unidades = select.parent().parent().find("[name*='-unidades']");
	var precio_total_neto = parseFloat($unidades.val())*parseFloat($precio_unitario.val())
	$precio_total_neto.val((precio_total_neto-(parseFloat(select.val())/100*precio_total_neto)).toFixed(2));
	get_total();
});