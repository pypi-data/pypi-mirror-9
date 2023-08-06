$(document).ready(function() {
	$("input[type='checkbox']").on("click",ignorar);

	function ignorar(){	
		var cliente_id= $(this).val()
		$.ajax({
			url:'/sms/ignorar/', 
			type : 'get', 
			data:{'cliente_id':cliente_id,}, 
			success: function(data){ 
				console.log(data.cliente)
			},
        	error: function() {
          		alert('Error');
          	},

		});
	};
});