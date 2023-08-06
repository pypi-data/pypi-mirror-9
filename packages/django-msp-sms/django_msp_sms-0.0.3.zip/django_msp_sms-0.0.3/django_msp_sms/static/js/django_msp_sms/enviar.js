$(document).ready(function() {

	$("#alert_danger").hide();
	$("#btn-abrirModal").show();
	$("#enviar").on("click",validar_sms)

	
	var porcentaje = 0 ;
	var numero_mensaje=1;
	var incorrectos=[];
	var mensajes;
	var correctos=0;

	function validar_sms(){	
		$("#enviar, #btn-abrirModal").attr('disabled','disabled');
		$("#btn-abrirModal").hide();
		var timer = setInterval(function (){	
			porcentaje = porcentaje + 1;	
	   		$('#progreso').attr('style',' width:'+porcentaje+'%');
	   		$('#progreso').text('Generando '+porcentaje+'%');
	   		if (porcentaje>95) { porcentaje-1;
	   			clearInterval(timer);	};
		},
		90);

		
		$.ajax({
			url:'/sms/validar_sms/', 
			type : 'get', 
			data:{}, 
			success: function(data){ 
				mensajes = data.mensajes;
				clearInterval(timer);
				$('#progreso').attr('style',' width:100%');				

				if (data.error != null) {
					$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
					$('#progreso').text('Créditos Insuficientes No se ha enviado Ningun Mensaje');
					alert(data.error); 
				}
				else{
					$('#progreso').text('Listo !!!');
					// alert('Listo para enviar Mensajes');
					$('#progreso').attr('style',' width:0%');
					clearInterval(timer);	
					enviar_sms();
				};
			},
        	error: function() {
          		$('#progreso').text('Error !!!');
				$('#progreso').attr('style',' width:100%');
				$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
				clearInterval(timer);
          	},

		});
	};

	function enviar_sms(){
		
		$.ajax({
			url:'/sms/enviar_sms/', 
			type : 'get', 
			data:{'mensaje':mensajes[(numero_mensaje-1)][1],
				'telefono':mensajes[(numero_mensaje-1)][0],
				'numero_mensaje':numero_mensaje,
			}, 

			success: function(data){ 
				console.log(mensajes[(numero_mensaje-1)][1]);
				numero_mensaje=data.numero_mensaje;
				console.log(data.resultado+'--'+data.telefono)
				if (data.resultado!='Mensaje enviado') {
					if (data.resultado == 'Apikey incorrecta' || data.resultado == 'Apikey no definido') {
						incorrectos.push(data.telefono+' = Llave errónea')
					}
					else{
						incorrectos.push(data.telefono+' = '+data.resultado);
					};
					
				}
				else{
					correctos+=1;
				};
				if (porcentaje<100) {					
					porcentaje=numero_mensaje/mensajes.length*100;
					$('#progreso').text('Enviando '+porcentaje.toFixed(2)+'%');
					$('#progreso').attr('style',' width:'+porcentaje+'%');
					enviar_sms();
				}
				else if (incorrectos.length > 0 ) {

					$("#alert_danger").show();

					incorrectos.forEach(function(incorrecto) {
						$("#alert_hijo").append(incorrecto+"<br/>");    							
					});
					alert(correctos+' Mensajes Enviados Correctamente');
					$("#enviar, #btn-abrirModal").attr('disabled',false);
				
				}
				else if(incorrectos.length == 0){
					$("#btn-abrirModal").hide();
					$('#progreso').attr('class','progress-bar progress-bar-success progress-bar-striped active ');
					$('#progreso').text('Enviados Correctamente');
					alert("Todos los mensajes se enviaron correctamente!!!");
					$("#enviar, #btn-abrirModal").attr('disabled',false);

				};
			}, 
			error: function() {
          		$('#progreso').text('Error !!!');
				$('#progreso').attr('style',' width:100%');
				$('#progreso').attr('class','progress-bar progress-bar-danger progress-bar-striped active ');
				clearInterval(timer);
			},
		});

		
		
		
	};

});