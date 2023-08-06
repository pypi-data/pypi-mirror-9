// $Id: publidoc.js 39e56a47a3fe 2014/05/04 11:46:31 Patrick $ 
// Publidoc

/*global jQuery: true */

jQuery(document).ready(function($) {
    // Hotspots
    var delay = 5000;
    $('.pdocHotspot').each(function() {
        var $hotspot = $(this);
        var $spot = $('#' + $hotspot.attr('id') + 's');
        var scenario = $hotspot.children('span').length;
        if ($spot.length && scenario) {
            $hotspot.css('opacity', 1);
            $hotspot.click(function() {
                if ($hotspot.css('opacity') == 1) {
                    $hotspot.animate({opacity: 0})
                        .delay(delay)
                        .animate({opacity: 1});
                    $spot.css({opacity: 0, display: 'block'})
                        .animate({opacity: 1})
                        .delay(delay)
                        .animate({opacity: 0}, function() {
                            $spot.css({opacity: '', display: ''});  
                        });
                } else {
                    $spot.click(); 
                }
            });

            $spot.click(function() {
                $spot.stop().animate({opacity: 0}, function() {
                    $spot.css({opacity: '', display: ''});  
                });
                $hotspot.stop().animate({opacity: 1});
            });
        }
    });
});
