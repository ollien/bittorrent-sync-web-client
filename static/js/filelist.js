var parentFolder	;
var readWrite = false;
var path = "";
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
		path+=name
		if (type=='folder'){
			loadFolder(name,secret);
			path+="/"
		}
		else{
			console.log(path)
			window.location.href = '/getFile'+path
			console.log(window.location.href)
		}
		
		// else if (type=="read/write"){
		// 	readWrite=true;
		// }
	});
}
function loadFolder(name,secret){
	$('#loading').show();
	args = {'secret':secret}
	console.log(name)
	console.log(name.indexOf('/')!=-1);
	if (name!=undefined && name!=null && name.indexOf('/')==-1){ //name.indexOf('/')==-1 is a hotfix for a problem where the files would not be avaliable if it was the root folder.
		args['path']=name;
	}
	console.log(args);
	$('#folderList').load('http://localhost:8080/folder #folderList',args,function(){
		$('#loading').hide();
		setupButtons();
		hideDeleted();
	});
}
function hideDeleted(){
	var items = $('.folderItem');
	for (var i=0; i<items.length; i++){
		if ($(items[i]).attr('state')=="deleted")
			$(items[i]).hide();
			// console.log(items[i]);
	}
}
$(document).ready(function(){
	setupButtons();
});