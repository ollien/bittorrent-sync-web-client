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
	$('#addSecret').click(function(event){
		$('#addSecretModal').modal('show');
	});
	$('#secretInput').popover({'trigger':'manual'});
	$('#dirInput').popover({'trigger':'manual'});
	$('#confirmAddSecret').click(function(event){
		var secret = $('#secretInput').val();
		var dir = $('#dirInput').val();
		if (dir.length!=0 && dir!='/'){
			
			var result; 
			// alert(dir);
			var checked = $('#createFolder').prop('checked');
			$.get('/dirExists',{'path':dir,'create':checked},function(data){
				if (data=='true'){
					result=true;
				}
				else if (data=='notAllowed'){
					result = -1;
				}
				else{
					result=false;
				}
				if (result===true && secret.length>0){
					$.post('/sync',{'method':'add_folder','dir':dir,'secret':secret},function(data){
						data = JSON.parse(data);
						if (data['error']!=0){
							var error=data['message'];
							$('#secretInput').attr('data-content',error);
							$('#secretInput').popover('show');
						}
						else{
							$('#dirInput').val('');
							$('#secretInput').val('');
							$('#secretInput').popover('hide');
							$('#dirInput').popover('hide');
							$('#addSecretModal').modal('hide');
							updateFolders();
						}
					});
				}
				else if (result===true && secret.length==0){
					$.post('/sync',{'method':'add_folder','dir':dir},function(data){
						data = JSON.parse(data);
						if (data['error']!=0){
							var error=data['message'];
							$('#dirInput').attr('data-content',error);
							$('#dirInput').popover('show');
						}
						else{
							$('#dirInput').val('');
							$('#secretInput').val('');
							$('#secretInput').popover('hide');
							$('#dirInput').popover('hide');
							$('#addSecretModal').modal('hide');
							updateFolders();
						}
					});
				}
				else if (result===false){
					$('#dirInput').attr('data-content',"This directory does not exist. You can create it manually or check the box below.");
					$('#dirInput').popover('show');
				}
				else{
					$('#dirInput').attr('data-content',"You do not have write permission to this directory.");
					$('#dirInput').popover('show');
				}
				
			});
			
			
		}
		else if (dir=='/'){
			$('#dirInput').attr('data-content',"You cannot choose / as your directory.");
			$('#dirInput').popover('show');
		}
	});
	$('#addSecretModal').keypress(function(event){
		if (event.which==13){
			$('#confirmAddSecret').click();
		}
	});
	$('#addSecretModal').on('hide.bs.modal',function(event){
		$('#secretInput').popover('hide');
		$('#dirInput').popover('hide');
	});
	$('#dirInput').on('input',function(event){
		$('#dirInput').popover('hide');
	});
	$('#secretInput').on('input',function(event){
		$('#dirInput').popover('hide');
	});
}
function hideDeleted(){
	var items = $('.folderItem');
	for (var i=0; i<items.length; i++){
		if ($(items[i]).attr('state')=="deleted")
			$(items[i]).hide();
	}
}
function secretInPage(){
	var items = $('.folderItem');
	for (var i=0; i<items.length; i++){
		if ($(items[i]).attr('secret')!="null"){
			return true;
		}
	}
	return false;
}
function updateFolders(){
	$('#folderList' ).load('/ #folderList');
}
$(document).ready(function(){
	if (!secretInPage()){
		$('#addSecret').css('visibility','hidden');
	}
	setupButtons();
	hideDeleted();
});