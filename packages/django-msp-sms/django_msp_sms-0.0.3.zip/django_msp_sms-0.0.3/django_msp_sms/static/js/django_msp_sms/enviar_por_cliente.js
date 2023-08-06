$(document).ready(function() {
	$("#btnEnviar-estadosCuenta").on("click", enviar_mensajes);
	$("#id_clientes_text").attr('class','form-control');

	var porcentaje = 0;
	var clientes;
	var correctos = [];
	var sin_mensajes =[];
	var clientes_sin_mensaje;
	var mensajes;
	var mensajes_enviados;
	var clientes_con_telefono_invalido= [];

	$("#alert").hide();
	$("#btnEnviar-estadosCuenta").show();

	function formPersonalizados_isValid(){
		var errors = [];
		var isValid = true;
		clientes = $("#id_clientes").val();

		if (clientes== null) {
			errors.push("Por favor selecciona almenos un cliente.");
			isValid = false;

		}
		
		if (isValid) {
			return true
		}

		return [false, errors]
	}

	function enviar_mensajes(){
		clientes = $("#id_clientes").val();
		if (clientes != null ){
			validar_mensajes();
		}else{
			alert('selecciona almenos un cliente');
		}
	}
	var timer;
	function validar_mensajes(index){
		$("#btnEnviar-estadosCuenta").hide();
		timer = setInterval(function (){	
			porcentaje = porcentaje + 1;	
	   		$('#progreso').attr('style',' width:'+porcentaje+'%');
	   		$('#progreso').text('Generando '+porcentaje+'%');
	   		if (porcentaje>95) { 
	   			clearInterval(timer);	
	   		};


		},90);

	  	clientes_ids = JSON.stringify($("#id_clientes").val());
	  	$.ajax({
			url:'/sms/validar_sms_clientes_ids/', 
			type : 'get', 
			data:{'clientes_ids':clientes_ids}, 
			success: function(data){ 
				mensajes = data.mensajes;
				clientes_sin_mensaje = data.clientes_sin_mensaje;
				$('#progreso').attr('style',' width:100%');				
				if (data.mensajes != null) {
					if (data.mensajes.length > 0){
						if (data.error != null) {
							$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
							$('#progreso').text('Créditos Insuficientes No se ha enviado Ningun Mensaje');
							$("#alert").show();
							$('#alert').attr('class','alert alert-danger fade in');
							$("#alertContainer").html(data.error);
							clearInterval(timer);
						}
						else{
							$('#progreso').attr('class','progress-bar progress-bar-striped active');
							$('#progreso').attr('style',' width:0%');			
							mensajes_enviados= 0;		
							enviar_mensaje(0);
						}
					}
					else{					
						$("#alert").show();
						$('#alert').attr('class','alert alert-danger fade in');
						$("#alertContainer").html('No hay mensajes para ninguno de los clientes seleccionados');
						$('#progreso').attr('class','progress-bar progress-bar-striped active');
						$('#progreso').text('');
						$('#progreso').attr('style',' width:0%');
						$("#id_clientes-deck").text("");
						$("#id_clientes").text("");
						$(".yourlabs-autocomplete autocomplete-light-widget").text("");
						clearInterval(timer);
					}
				}
			},
			error: function() {
          		$('#progreso').text('Error !!!');
				$('#progreso').attr('style',' width:100%');
				$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
				clearInterval(timer);
			},
		});

	}

	function enviar_mensaje(index){
		porcentaje = (index +1 ) * 100 / mensajes.length;
		$('#progreso').attr('style',' width:'+porcentaje+'%');
	  	$('#progreso').text('Enviando '+porcentaje+'%');

	  	var telefono = mensajes[index][0]
	  	var mensaje = mensajes[index][1]
	  	console.log(mensaje);
	  	$.ajax({
			url:'/sms/enviar_mensaje/', 
			type : 'get', 
			data:{'telefono':telefono, 'mensaje':mensaje}, 
			success: function(data){ 
				mensajes_enviados = mensajes_enviados + 1;
				if (mensajes != null) {
					if (index < (mensajes.length-1)) {
						enviar_mensaje(index+1);					
					}
					else{
						$("#alert").show();
						$('#alert').attr('class','alert alert-info fade in');
						var mensaje_alerta = mensajes_enviados+" Mensajes Enviados correctamente.<br>"
						if (clientes_sin_mensaje.length>0) {
							mensaje_alerta =mensaje_alerta +"<br><strong>Clientes sin cargos:</strong><br>"+clientes_sin_mensaje.join('<br/>');
						}
						if (clientes_con_telefono_invalido.length>0) {
							mensaje_alerta =mensaje_alerta +"<br><strong>Clientes con telefono invalido:</strong><br>"+clientes_con_telefono_invalido.join('<br/>');
						}

						$("#alertContainer").html(mensaje_alerta); 
						$('#progreso').attr('class','progress-bar progress-bar-striped active');
						$('#progreso').text('Enviados 100%');
						alert("Mensajes Enviados");

						$('#progreso').text('');
						$('#progreso').attr('style',' width:0%');
						$("#id_clientes-deck").text("");
						$("#id_clientes").text("");
						$(".yourlabs-autocomplete autocomplete-light-widget").text("");

						clearInterval(timer);
						$("#btnEnviar-estadosCuenta").show();
						
					}

				}
			}, 
		});
	}
	
});