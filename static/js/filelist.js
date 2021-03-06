var parentFolder	;
var uploading = false;

function setupButtons(){
	$('a.fileItem').click(function(event){
		event.stopPropagation();
		var name = $(this).attr('name');
		window.location.href = '/getFile'+createPath()+'/'+name
		event.preventDefault();
	
	});
	$('core-icon.secretIcon').click(function(event){
		event.stopPropagation();
		var input = $(this).parent().find("> .folderSecret");
		if ($(input).width()==0) {
			$(input).animate({
					width:'200px'
			},
			{
					duration:150,
					specialEasing:{
						width:"linear"
					}
				});
			$(input).focus();
		}
		});
	$('.folderSecret').focus(function(event){
		event.stopPropagation();
		$(this).attr("type","text");
		$(this).select();
	});

	$('.folderSecret').blur(function(event){
		$(this).attr("type","password");
		if ($(this).width()>0){
			$(this).animate({
					width:'0px'
			},
			{
					duration:150,
					specialEasing:{
						width:"linear"
					}
				});
		}
	});
	$('#addSecret').click(function(event){
		$('#addSecretModal')[0].toggle();
		$('#dirInput').val("");
		$('#secretInput').val("");
		setValid('#addSecretModal','#confirmAddSecret');
	});
	$('#confirmAddSecret').click(function(event){
		// $('#dirInput')[0].setCustomValidity('Your mother was a hamster');
		// $('#secretInput')[0].setCustomValidity('Your father smelled of elderberries');
		var secretInp = $('#secretInput');
		var dirInp = $('#dirInput');
		if (secretInp.length > 0 && dirInp.length > 0){
			if (!secretInp[0].checkValidity() && !dirInp[0].checkValidity()){
				return;
			}
		}
		var secret = $('#secretInput').val();
		var dir = $('#dirInput').val();
		if (dir==='/'){
			var inp = $('#dirInput');
			if (inp.length > 0){
				inp[0].setCustomValidity("The root directory cannot be chosen.")
			}
		}
		else{
			var checked = $('#createFolder').prop('checked');
			$.get('/dirExists',{'path':dir,'create':checked},function(data){
				console.log(data);
				if (data=='true'){
					result = true;
				}
				else if (data=='notAllowed'){
					result = -1;
				}
				else{
					result = false;
				}
				console.log(result);
				if (result===true){
					$.post('/sync',{'method':'add_folder','dir':dir,'secret':secret},function(data){
						data = JSON.parse(data);
						if (data['error']!=0){
							var error=data['message'];
							$('#secretInput')[0].setCustomValidity(error);
							$('#confirmAddSecret').prop('disabled',true);
						}
						else{
							$('#addSecretModal')[0].toggle();
						}
					});
				}
				else if (result===-1){
					$('#dirInput')[0].setCustomValidity("You don't have permission to write to this directory");
					$('#confirmAddSecret').prop('disabled',true);
				}
				else if (result===false){
					$('#dirInput')[0].setCustomValidity("This directory does not exist. You can create it by checking the below box.");
					$('#confirmAddSecret').prop('disabled',true);
				}
			})
		}
	});
	
	$('#upload').change(function(event){
		var fileList = $('#upload')[0].files
		var path = createPath()+fileList[0].name
		var fileName = fileList[0].name
		console.log(path)
		if (fileList.length==1){
			$('#uploadModal').attr('autoCloseDisabled',true);
			$('#cancelUpload').prop('disabled',true);
			$.get('/file_exists',{'path':path},function(data){
				if (data=='false'){
					$('#uploadStatus').removeClass('error');
					$('#uploadStatus').text('');
					$('#uploadSpinner').show();
					$('#uploadSpinner').attr('active','true');
					//JSON likes to not handle files correctly, so we use FormData
					data = new FormData()
					data.append('path',path);
					data.append('f',fileList[0]);
					$.ajax({
						url:'/upload',
						type:'POST',
						data:data,
						processData:false,
						contentType:false,
						success:function(data){
							$('#cancelUpload').prop('disabled',false);
							$('#uploadModal').attr('autoCloseDisabled',false);
							$('#uploadModal')[0].toggle();
							$('#uploadSpinner').attr('active','false');
							$('#uploadSpinner').hide();
							updateFolders();
							//Quick hack to reset the upload field,stolen from stackoverflow
							$('#upload').wrap('<form>').parent('form').trigger('reset');
							$('#upload').unwrap();
							var p = createPath();
							p = p.replace(/\/+/,'/');
							$('#fileUploadedToast').attr("text",fileName+" has successfully uploaded to "+p+".");
							$('#fileUploadedToast')[0].show();
						}
					});
				}
				else{
					if ($('#uploadStatus').hasClass('error')){
						$('#uploadStatus').removeClass('error');
					}
					$('#uploadStatus').text("This file already exists. Either rename the file you are uploading or choose another file.");
					$('#uploadStatus').addClass('error');
				}
			});
		}
		
	});
	$('#uploadFile').click(function(event){
		$('#uploadModal')[0].toggle();
	});
	
	$('core-icon.deleteIcon').click(function(event){
		event.stopPropagation();
		var item = $(this).parent().attr('label');
		$('#deleteFilename').text(item);
		$('#deleteModal')[0].toggle();
		
	});
	$('#confirmDelete').click(function(event){
		event.stopPropagation();
		var item = $('#deleteFilename').text()
		var fullPath = createPath()+"/"+item;
		$.post('/delete',{'path':fullPath},function(data){
			data = JSON.parse(data);
			if (data['error']==0){				
				$('#deleteModal')[0].toggle();
				$('#fileDeletedToast').attr("text",item+" has been deleted.");
				$('#fileDeletedToast')[0].show();
				updateFolders();
			}
			else{
				console.log("Error deleting.")
			}
		});
		
	});
	$('core-icon.publicIcon').click(function(event){
		event.stopPropagation();
		var item = $(this).parent().attr('label');
		var fullPath = createPath()+item;
		console.log(fullPath);
		$.post('/makePublic',{'path':fullPath},function(data){
			data = JSON.parse(data);
			if (data['error']==0){
				$('#publicName').text(item);
				$('#publicURL').val(window.location.origin+data['url']);
				$('#publicModal')[0].toggle();
			}
			else{
				console.log('Error making public.');
			}
		});
	});
	
}
function createPath(){
	if (window.location.pathname.indexOf('/folder/') > -1)
		return window.location.pathname.split('/folder/').join('/');
	return window.location.pathname
}
function hideDeleted(){
	var items = $('.folderItem');
	for (var i=0; i<items.length; i++){
		if ($(items[i]).attr('state')=="deleted"){
			$(items[i]).hide();
		}
	}
}
function secretInPage(){
	var items = $('.folderItem');
	for (var i=0; i<items.length; i++){
		if ($(items[i]).attr('secret')!="null"){
			return $(items[i]).attr('secret');
		}
	}
	return null;
}
function isRoot(){
	if (window.location.pathname=='/'){
		return true;
	}
	return false;
}
function updateFolders(){
	$('#folderList' ).load(window.location.pathname+' #folderList',function(){		
		setupButtons();
		hideDeleted();
		outputLength = $('#folderList');	
	});
	
}
function getPing(){
	var time = new Date().getTime();
	$.ajax({
		type: "GET",
		url: '/hello',
		async: false
	});
	return new Date().getTime() - time;
}
function setValid(s,button){
	console.log(s,button);
	if (s[0]!='#')
		s='#'+s;
	if (button[0]!='#')
		button='#'+button;
	var q = $(s);
	if (q.length > 0){
		var inputs = q.find('paper-input');
		var valid = true;
		for (var i=0; i<inputs.length; i++){
			if (!inputs[i].checkValidity()){
				inputs[i].setCustomValidity('');
			}
			// Check again to see if we still need to gray it out
			if (!inputs[i].checkValidity()){
				valid = false;
			}
		}
		if (!valid){
			$(button).prop("disabled",true);
		}
		else{
			$(button).prop("disabled",false);
		}
		
	}
}
//stolen from stackoverflow (http://stackoverflow.com/questions/202605/repeat-string-javascript) by Peter Bailey, allows me to repeat strings.
String.prototype.repeat = function(num)
{
	return new Array( num + 1 ).join(this);
}
$(document).ready(function(){
	if (window.location.href[window.location.href.length-1]!='/'){
		window.location.href+='/';
	}
	if (!isRoot()){
		$('#addSecret').hide();
	}
	else{
		$('#uploadFile').hide();
	}
	setupButtons();
	hideDeleted();
	outputLength = $('#folderList').length;
});
