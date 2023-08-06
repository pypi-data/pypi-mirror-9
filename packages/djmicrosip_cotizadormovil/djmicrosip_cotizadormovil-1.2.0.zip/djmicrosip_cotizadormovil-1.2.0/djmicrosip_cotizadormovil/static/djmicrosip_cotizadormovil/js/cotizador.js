var $total = $("#total");
var $subtotal = $("#subtotal");
var $descuento = $("#descuento");
var $descuentop = $("#descuentop");
var $descuento_tp = $("#descuento_tp");
var $total_con_descuento = $("#total_con_descuento");
var moneda_id = $("#select_monedas").val();
var lista_precios_id = $("#select_lista_precios").val();

$(document).ready(function(){
	$("#modal-button").attr("disabled",true);
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
	$("[name*='-articulo-autocomplete']").attr("class","form-control");
	$(".delete-row").find("i").attr("class","glyphicon glyphicon-trash");
}

function get_total(){
	var total = 0;
	var subtotal = 0;
	$("[name*='-precio_total_neto']").each(function(){
		if ($(this).val() != '')
		{
			total += parseFloat($(this).val());
			var precio_unitario = parseFloat($(this).parent().parent().find("[name*='-precio_unitario']").val());
			var unidades = parseFloat($(this).parent().parent().find("[name*='-unidades']").val());
			subtotal += unidades*precio_unitario;
		};
		
	});
	var descuento = subtotal - total;
	$total.text(total.toFixed(2));
	$subtotal.text(subtotal.toFixed(2));
	$descuento.text(descuento.toFixed(2));
	if ((subtotal-total)<0.01)
	{
		$(".sub").hide();
		$(".des").hide();
	}
	else
	{
		$(".sub").show();
		$(".des").show();
	};
	if (total=0)
	{
		$(".descuento_tp").hide();
		$(".total_con_descuento").hide();
	};
}

$("[name*='-descuento']").on("input",function(){
	if ($(this).val() == '') 
	{ 
		$(this).val(0);
		$(this).select();
	};
	var select = $(this);
	var $precio_unitario = select.parent().parent().find("[name*='-precio_unitario']");
	var $precio_total_neto = select.parent().parent().find("[name*='-precio_total_neto']");
	var $unidades = select.parent().parent().find("[name*='-unidades']");
	var precio_total_neto = parseFloat($unidades.val())*parseFloat($precio_unitario.val())
	$precio_total_neto.val((precio_total_neto-(parseFloat(select.val())/100*precio_total_neto)).toFixed(2));
	get_total();
	$("#descuentop").trigger("input");
});

$("#descuentop").on("input",function(){
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
	// $("#select_monedas").attr("disabled",true);
	$("select[name*='-articulo']").trigger("change");
	$("#descuentop").trigger("input");
	if ($(this).val() == '-')
	{
		$(this).val(moneda_id);
	}
	$("#cotiza").show();
	foco_detalle();
	$("#id_tipo_cambio_d").attr("disabled",true);
	moneda_id = $(this).val();
	get_total();

});

//AL CAMBIAR LA LISTA DE PRECIOS
$("#select_lista_precios").on("change",function(){
	if ($("#cotiza").is(":visible"))
	{
		$("select[name*='-articulo']").trigger("change");
	};
	if ($(this).val() == '-')
	{
		// $("#modal-button").attr("disabled",true);
		$(this).val(lista_precios_id);
	}
	else
	{
		$("#modal-button").attr("disabled",false);
	};
	lista_precios_id = $(this).val();	
	
});

// Al Seleccionar el articulo
$("select[name*='-articulo']").on("change",function(){
	var articulo_id = $(this).val();
	var select = $(this);
	var $precio_unitario = select.parent().parent().parent().parent().parent().parent().find("[name*='-precio_unitario']");
	var $precio_total_neto = select.parent().parent().parent().parent().parent().parent().find("[name*='-precio_total_neto']");
	var $unidades = select.parent().parent().parent().parent().parent().parent().find("[name*='-unidades']");
	var $existencia = select.parent().parent().parent().parent().parent().parent().find("[name*='-existencia']");
	var $clave = $(this).parent().parent().parent().find("[name*='-clave']");
	


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
	 	   		$existencia.text(data.existencia);
	 	   		$precio_unitario.select();
	 	   		get_total();
	 	   		$clave.parent().removeClass();
	 	   		$clave.hide();
	 	   		select.parent().parent().attr("class","col-xs-12")
				$("[name*='-descuento']").trigger("input");
				$("#descuentop").trigger("input");
	 	   		if (data.existencia <= 0)
	 	   		{
	 	   			$existencia.attr("style","color: rgb(192, 29, 29);");
	 	   		};
			},
		});
	}
	else
	{
		$unidades.val(1);
		$precio_total_neto.val(0);
		$precio_unitario.val(0);
		$clave.parent().addClass("col-xs-4");
   		$clave.show();
   		select.parent().parent().attr("class","col-xs-8");
   		$clave.focus();
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
	$("[name*='-descuento']").trigger("input");
	get_total();
});


//Al presionar F8 en la caja de texto de articulo se despliega el modal para ver existencias
$("[name*='-articulo-autocomplete']").on("keydown",function(e){
	if (e.keyCode == 119) {
        	$('#myModal').modal();
        }
});

setInterval(function(){	$(".yourlabs-autocomplete").find("span").attr("style","line-height:30px") }, 1);

$("#buscar-modal").on("click",function(){
	$("#buscar-modal").attr("disabled",true);
	var nombre = $("#modal-nombre").val();
	var clave = $("#modal-clave").val();
	$.ajax({
 	   	url:'/cotizadorm/articulos_search/',
 	   	type : 'get',
 	   	data : {
 	   		'lista_precios_id':lista_precios_id,
 	   		'clave':clave,
 	   		'nombre':nombre,
 	   	},
 	   	success: function(data){
 	   		if (data.articulos.length > 0)
 	   		{
	 	   		$('#articles_table').find('tbody').html('');
	 	   		data.articulos.forEach(function(articulo) {
					$('#articles_table').find('tbody').append( "<tr> <td> "+articulo[2]+" </td> <td id='nombre'>"+  articulo[1]+"</td> <td>"+articulo[4]+"</td><td>"+parseFloat(articulo[3]).toFixed(2)+" <small>"+ articulo[5]+"</small></td><td> <button class='btn btn-default add'><i class='glyphicon glyphicon-plus'></i><input type='hidden' value='"+articulo[0]+"'> </a> </td> </tr>" );	
					
				});

				
				$(".add").on("click",function(){
					var articulo_id = $(this).find("input").val();
					var articulo_nombre = $(this).parent().parent().find("#nombre").text();
					$articulo = $("input[name*='-articulo']").last();
					cargar_articulo($articulo,articulo_id,articulo_nombre);
					$("#myModal").modal("hide");
					$('#articles_table').find('tbody').html('');
					$("#modal-clave").val("");
					$("#modal-nombre").val("");
					$(this).parent().parent().find("input[name*='-precio_unitario']").focus();

				});
 	   		}
 	   		else
 	   		{
 	   			$('#articles_table').find('tbody').html('');
 	   			alert("No hay articulos");
 	   		};
 	   		$("#buscar-modal").attr("disabled",false);

 	   		
 	   	},
	});
});

$('#myModal').on('shown.bs.modal', function () {
    $('#modal-clave').focus();
    if (!$("input[name*='-articulo-autocomplete']").last().is(":visible"))
    {
    	$(".btn-success").trigger("click");
    };
});

$("#crear_documento").on("click",function(){
	var tipo_cambio = $("#id_tipo_cambio_d").val();
	var descuento_porcentaje = $("#descuentop").val();
	var lista = [];
	$("#id_detalles_data").find("tbody tr").each(function(){
		var detalle = []
		var articulo_id = $(this).find("select[name*='-articulo']").val();
		detalle.push(articulo_id[0]);
		var precio_unitario = $(this).find("[name*='-precio_unitario']").val();
		detalle.push(precio_unitario);
		var porcentaje_dscto = $(this).find("[name*='-descuento']").val();
		detalle.push(porcentaje_dscto);
		var precio_total_neto = $(this).find("[name*='-precio_total_neto']").val();
		detalle.push(precio_total_neto);
		var unidades = $(this).find("[name*='-unidades']").val();
		detalle.push(unidades);
		lista.push(detalle);
	});
	$.ajax({
 	   	url:'/cotizadorm/crea_documento/',
 	   	type : 'get',
 	   	data : {
 	   		'moneda_id':$("#select_monedas").val(),
 	   		'lista':JSON.stringify(lista),
 	   		'tipo_cambio': tipo_cambio,
 	   		'descuento_porcentaje':descuento_porcentaje,
 	   	},
 	   	success: function(data){
 	   		var modulo = data.modulo;
 	   		var documento_folio = data.documento_folio;
 	   		if (modulo != '')
 	   		{
 	   			alert("Se Creo el Documento con folio "+documento_folio+" en el modulo de "+modulo);
 	   		}
 	   		else
 	   		{
 	   			alert("Las preferencias tienen  definido no integrar\nNo se Guardo ningun documento.");
 	   		};
 	   	},
 	   	error:function(){
 	   		alert("Error");
 	   	},
	});
});