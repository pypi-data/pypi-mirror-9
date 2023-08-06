function qs(key) {
	key = key.replace(/[*+?^$.\[\]{}()|\\\/]/g, "\\$&"); // escape RegEx meta chars
	var match = location.search.match(new RegExp("[?&]" + key + "=([^&]+)(&|$)"));
	return match && decodeURIComponent(match[1].replace(/\+/g, " "));
}

(function ($) {
	$(document).ready(function () {
		var $fullpath = $('.localdir').attr("data-fullpath");
		var $dirs = $('.localdir .dir a');
		var $select = $('.localdir #select');
		var $up_link = $('a#up');

		$up_link.click(function(){
			var $this = $(this);
			$this.attr('href', $this.attr('href') + document.location.search);
		});

		$dirs.bind({
			'click': function (event) {
				var $this = $(this);
				if (!$(this).hasClass('seleted')) {
					$dirs.removeClass('selected');
					$this.addClass('selected');
				}
				$select.text($select.attr('data-select-text'));
				event.preventDefault();
			},
			'dblclick': function() {
				document.location = $(this).attr('href') + document.location.search;
			}
		});

		$select.click(function () {
			var $value = $('.localdir .dir .selected') || $fullpath;
			var $target = $(opener.document).find('#'+qs('id'));
			$target.val($fullpath + '/' + $value.text()).attr('popup_url', document.location.pathname);
		})
	});
})(window.django ? django.jQuery : jQuery);