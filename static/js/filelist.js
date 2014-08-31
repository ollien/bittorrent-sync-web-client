var parentFolder	;
var readWrite = false;
function setupButtons(){
	$('.folderItem').click(function(event){
		var t = $(this);
		console.log($(t).attr('type'));
		console.log($(this).attr('type'));
		var type = $(this).attr('type');
		var name = $(this).attr('name');
		var secret = $(this).attr('secret');
		console.log(name)
		if (secret=="null"){
			secret = parentFolder;
		}
		else{
			parentFolder = secret;
		}
		if (type=='folder'){
			// loadFolder(name,secret);
			if (name[0]=='/'){
				name=name.substring(1,name.length);
			}
			if (window.location.href[window.location.href.length-1]=='/'){
				if (window.location.href.indexOf('/folder/')==-1){
					window.location.href+='folder/'+name
				}
				else{
					window.location.href+=name;
				}
			}
				
			else
				window.location.href+='/'+name;
		}
		else{
			var path = window.location.href.split('/');
			var temp = []
			for (var i=path.indexOf("folder")+1; i<path.length; i++){
				temp.push(path[i]);	
			}
			temp.push(name);
			path=temp.join('/')
			window.location.href = '/getFile/'+path
			console.log(window.location.href)
		}
		
		// else if (type=="read/write"){
		// 	readWrite=true;
		// }
	});
	$('.folderSecret').click(function(event){
		event.stopPropagation();
		$(this).attr("type","text");
	});
	$('.folderSecret').blur(function(event){
		$(this).attr("type","password");
	});
}
function hideDeleted(){
	var items = $('.folderItem');
	for (var i=0; i<items.length; i++){
		if ($(items[i]).attr('state')=="deleted")
			$(items[i]).hide();
	}
}
$(document).ready(function(){
	setupButtons();
	hideDeleted();
});