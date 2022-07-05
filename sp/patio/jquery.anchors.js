(function($){

$.fn.scrollAnchors = function(options) {
var settings = { duration: 1, easing: "swing" };
  if (options) $.extend(settings,options);
  return $(this).click(function(event) {
    event.preventDefault();
    var target_offset = 
        $("a[name="+this.hash.slice(1)+"]").offset();
    var target_top = target_offset.top;
    $('html, body').animate({scrollTop:target_top}, 
        settings.duration, settings.easing);
  });
}

})(jQuery);
