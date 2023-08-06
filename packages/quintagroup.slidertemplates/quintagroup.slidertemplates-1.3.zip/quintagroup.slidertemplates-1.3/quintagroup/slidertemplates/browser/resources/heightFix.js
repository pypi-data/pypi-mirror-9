$(document).ready(function() {
	setTimeout(function(){
		var listHeight = $(".resp-vtabs .resp-tabs-list").height();
		$(".resp-vtabs .resp-tabs-container").css({'min-height':listHeight});
	}, 1);
});