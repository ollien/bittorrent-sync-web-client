$(document).ready(function(){
	$('#loading').show();
	$('#folderList').load('http://localhost:8080/folder #folderList',{'secret':'AGSCU2RBBXQRDC6PGMLYMZH6AHVRDMMID'},function(){
		$('#loading').hide();
	})
});