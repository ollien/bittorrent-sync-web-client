$(document).ready(function(){
	$.ajax({
		'url':'/sync',
		// 'data':{'method':'get_folders'},
		'data':{'method':'get_files','secret':'AGSCU2RBBXQRDC6PGMLYMZH6AHVRDMMID'},
		'success':function(data){
			console.log(data)
			console.log('done')
		}
		});
});