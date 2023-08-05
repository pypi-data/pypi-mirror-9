if (djinn === undefined) {
    var djinn = {};
}


if (djinn.i18n === undefined) {
  djinn.i18n = {};
}


/**
 * Determine position of menu. Shamelessly copied from
 * bootstrap-contextmenu.
 */
djinn.i18n.getPosition = function(e, menu) {

	var mouseX = e.clientX, mouseY = e.clientY;
	var boundsX = $(window).width(), boundsY = $(window).height();

	var menuWidth = menu.outerWidth();
	var menuHeight = menu.outerHeight();

	var tp = {"position": "absolute"};
	var Y, X, parentOffset;
  
	if (mouseY + menuHeight > boundsY) {
		Y = {"top": mouseY - menuHeight + $(window).scrollTop()};
	} else {
		Y = {"top": mouseY + $(window).scrollTop()};
	}
  
	if ((mouseX + menuWidth > boundsX) && ((mouseX - menuWidth) > 0)) {
		X = {"left": mouseX - menuWidth + $(window).scrollLeft()};
	} else {
		X = {"left": mouseX + $(window).scrollLeft()};
	}
  
	// If context-menu's parent is positioned using absolute or relative
	// positioning, the calculated mouse position will be incorrect.
	// Adjust the position of the menu by its offset parent position.
	parentOffset = menu.offsetParent().offset();
	X.left = X.left - parentOffset.left;
	Y.top = Y.top - parentOffset.top;

  // adjust
  Y.top -= 50;
  X.left -= 30;
  
	return $.extend(tp, Y, X);
};


$(document).ready(function() {

  $("#ctxmenu .close").click(function(e) {
    e.preventDefault();
    $("#ctxmenu").hide();
  });

  $("[data-msgid]").each(function(idx, elt) {

    elt = $(elt);

    $(document).on("contextmenu", "[data-msgid]", function(e) {

      e.preventDefault();

      return false;
    });

    $(document).on("mousedown", "[data-msgid]", function(e) {

      if (e.button == 2) { 

        e.preventDefault();
        
        var tgt = $(e.currentTarget);
        
        var msgid = tgt.data("msgid");

        $("#ctxmenu ul").html(
          '<li><a class="modal-action" href="/djinn/i18n/trans/' + msgid + '/">Translate \'' + msgid + '\'</a></li>');

        $("#ctxmenu").css(djinn.i18n.getPosition(e, $("#ctxmenu")));

        $("#ctxmenu").show();
        
        return false;
      } 
    });
  });
});
