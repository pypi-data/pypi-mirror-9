/*global jQuery */

(function(window, $) {
	'use strict';

	$(function() {
    $('.logout-and-close-link').click(function() {
      var closeWindow = function() {
        if (typeof window.opener === 'object' && window.opener instanceof Window) {
          window.close();
        }
        else {
          bootbox.alert('Please close this window manually.');
        }
      };

      if ($(this).attr('href') && $(this).attr('href') != '#') {
        $.get($(this).attr('href'), function(data) {
          if (data == 'OK') {
            closeWindow();
          }
        });
      }
      else {
        closeWindow();
      }

      return false;
    });

    $('.logout-display-toggle-link').click(function(e) {
      $('#logout-display').toggle();

      return false;
    });
  });
})(window, jQuery);
