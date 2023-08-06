var favorites = {};

favorites.init = function(){
	$('.favorite-button').hover(function(){
		$(this).find('img').toggle();
	})
}

$(document).ready(favorites.init);