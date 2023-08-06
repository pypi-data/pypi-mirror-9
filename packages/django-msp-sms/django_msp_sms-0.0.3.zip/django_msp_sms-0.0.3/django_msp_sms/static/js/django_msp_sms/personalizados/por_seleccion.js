$(document).ready(function() {
	$("#btnEnviar-personalizado").on("click", personalizados_checarSaldo);

	var porcentaje = 0;
	var clientes;
	var correctos = [];
	var sin_mensajes =[];
	var clientes_sin_mensaje;
	var mensajes;
	var mensajes_enviados;
	var mensaje_personalizado;
	var clientes_con_telefono_invalido= [];

	$("#alert").hide();
	$("#btnEnviar-personalizado").hide();
	$("#texarea-mensaje").hide();
	
	function formPersonalizados_isValid(){
		var errors = [];
		var isValid = true;
		clientes = $("#id_clientes").val();
		mensaje_personalizado = $("#texarea-mensaje").val();

		if (clientes== null) {
			errors.push("Por favor selecciona al menos un cliente.");
			isValid = false;

		}
		if (mensaje_personalizado == "") {
			errors.push("Por favor escribe el mensaje a enviar.");	
			isValid = false;
		};

		if (isValid) {
			return true
		}

		return [false, errors]
	}

	function personalizados_checarSaldo(){
		clientes = $("#id_clientes").val();
		mensaje_personalizado = $("#texarea-mensaje").val();
		form_isValid = formPersonalizados_isValid();
		if (form_isValid ==  true) {
			$.ajax({
				url:'/sms/get_creditos/', 
				type : 'get', 
				success: function(data){ 
					var creditos_disponibles = data.creditos;
					if (creditos_disponibles < clientes.length) {
						$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
						$('#progreso').text('Créditos Insuficientes No se ha enviado Ningun Mensaje');
						$("#alert").show();
						$('#alert').attr('class','alert alert-danger fade in');
						$("#alertContainer").html("Creditos Insuficientes.<br/>Creditos Disponibles: "+ creditos_disponibles+"<br/>Mensajes por enviar: "+ clientes.length);
					}
					else{
						clientes_ids = JSON.stringify($("#id_clientes").val());
						$.ajax({
							url:'/sms/get_mensajes_personalizados/', 
							type : 'get', 
							data:{'clientes_ids':clientes_ids, 'mensaje':mensaje_personalizado,}, 
							success: function(data){
								mensajes = data.mensajes;
								clientes_con_telefono_invalido = data.clientes_con_telefono_invalido;
								clientes_sin_mensaje = [];
								$('#progreso').attr('class','progress-bar progress-bar-striped active');
								$('#progreso').attr('style',' width:0%');			
								mensajes_enviados= 0;	
								enviar_mensaje(0);
								$("#alertContainer").append("Clientes con telefono invalido:<br/>");
								if (clientes_con_telefono_invalido.length>0){
									clientes_con_telefono_invalido.forEach(function(cliente) {
										$("#alertContainer").append(cliente+"<br/>");
									});
								}
							}, 
						});
					}

				}, 
	        	error: function() {
	          		$('#progreso').text('Error !!!');
					$('#progreso').attr('style',' width:100%');
					$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
					clearInterval(timer);
				},
			});
		}else{
			var errors = form_isValid[1];

			$("#alert_danger").show();
			$("#alertContainer").html("");
			$('#alert').attr('class','alert alert-danger fade in');
			errors.forEach(function(error) {
				$("#alertContainer").append(error+"<br/>");
			});
			$("#alert").show();
		}


		


	}

	var timer;
	function validar_mensajes(index){
		timer = setInterval(function (){	
			porcentaje = porcentaje + 1;	
	   		$('#progreso').attr('style',' width:'+porcentaje+'%');
	   		$('#progreso').text('Generando '+porcentaje+'%');
	   		if (porcentaje>95) { porcentaje-1;
	   			clearInterval(timer);	};
		},
		90);
	  	clientes_ids = JSON.stringify($("#id_clientes").val());
	  	$.ajax({
			url:'/sms/validar_sms_clientes_ids/', 
			type : 'get', 
			data:{'clientes_ids':clientes_ids}, 
			success: function(data){ 
				mensajes = data.mensajes;
				clientes_sin_mensaje = data.clientes_sin_mensaje;
				$('#progreso').attr('style',' width:100%');				
				if (data.mensajes.length > 0){
					if (data.error != null) {
						$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
						$('#progreso').text('Créditos Insuficientes No se ha enviado Ningun Mensaje');
						$("#alert").show();
						$('#alert').attr('class','alert alert-danger fade in');
						$("#alertContainer").html(data.error);
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
				};
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
					$("#texarea-mensaje").val("");

					$('#progreso').text('');
					$('#progreso').attr('style',' width:0%');
					$("#id_clientes-deck").text("");
					$("#id_clientes").text("");
					$(".yourlabs-autocomplete autocomplete-light-widget").text("");

					clearInterval(timer);
					$("#btnEnviar-personalizado").show();
					
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
	
});