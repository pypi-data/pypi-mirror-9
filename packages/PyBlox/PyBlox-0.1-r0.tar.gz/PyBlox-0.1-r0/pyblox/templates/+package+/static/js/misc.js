
// jQuery for page scrolling feature - requires jQuery Easing plugin
var cbpAnimatedHeader = (function() {

	var docElem = document.documentElement,
		header = document.querySelector('.navbar-fixed-top'),
		didScroll = false,
		changeHeaderOn = 300;

	function init() {
		window.addEventListener('scroll', function(event) {
			if(!didScroll) {
				didScroll = true;
				setTimeout( scrollPage, 250 );
			}
		}, false);
	}

	function scrollPage() {
		var sy = scrollY();
		if (sy >= changeHeaderOn) {
			classie.add(header, 'navbar-shrink');
		}
		else {
			classie.remove(header, 'navbar-shrink');
		}
		didScroll = false;
	}

	function scrollY() {
		return window.pageYOffset || docElem.scrollTop;
	}
	init();
})();

$(function() {
    $('.page-scroll a').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
});

// Highlight the top nav as scrolling occurs
$('body').scrollspy({
    target: '.navbar-fixed-top'
});

// Closes the Responsive Menu on Menu Item Click
$('.navbar-collapse ul li a').click(function() {
    $('.navbar-toggle:visible').click();
});

// When the window has finished loading create our google map below
google.maps.event.addDomListener(window, 'load', initmap);

function initmap() {

    var mapOptions = {
        zoom: 11,

        // The latitude and longitude to center the map (always required)
        center: new google.maps.LatLng(32.7758, -96.7967),

        styles: [{
            featureType: "all",
            elementType: "all",
            stylers: [
                {invert_lightness: true},
                {saturation: 10},
                {lightness: 30},
                {gamma: 0.5},
                {hue: "#4896da"}
            ]
        }]
    };
    var mapElement = document.getElementById('map');
    var map = new google.maps.Map(mapElement, mapOptions);
}