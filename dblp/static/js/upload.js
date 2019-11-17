$(window).bind("load", function() {
	$('#btnUpload').click(function(){
		$('#clickTitle').hide()
		$('#btnUpload').hide()
		$('.hide').show()
		$.ajax({
			type: 'POST',
			url: '/upload',
		});
	});

	
    var source = new EventSource("/progress");
	source.onmessage = function(event) {
		$('.progress-bar').css('width', event.data+'%').attr('aria-valuenow', event.data);
		$('.progress-bar-label').text(event.data+'%');
		if(event.data == 100){
			source.close()
		}
	}
 });
