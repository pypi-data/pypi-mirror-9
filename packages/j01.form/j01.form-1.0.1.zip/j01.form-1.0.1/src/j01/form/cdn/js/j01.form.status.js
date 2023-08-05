/* j01.form.status.js */
(function($) {
$.fn.j01FormStatus = function(o) {
    // add status bar based on form field input values
    o = $.extend({
        target: '#j01FormStatus',
        check: true
    }, o);

    var widgets = [];

    function showStatus(seen) {
        var s = seen.length;
        var w = widgets.length;
        var width = s / w * 100 + "%"
        $(o.target).css('width', width);
    }

    function checkStatus(e) {
        var seen = [];
        for (var n = widgets.length; n--;) {
            var widget = widgets[n];
            type = widget.attr("type");
            tagName = widget.prop("tagName").toLowerCase();
            if ((type === 'text' || type === 'password' ||
                type === 'radio' || type === 'checkbox' ||
                tagName === 'textarea') && widget.val()) {
                // value given, push to seen array
                seen.push(widgets[n]);
            } else if (tagName === 'select' && widget.prop("selectedIndex") > 0) {
                // value given, push to seen array
                seen.push(widgets[n]);
            }
        }
        showStatus(seen);
    }

    function setUpWidgets(form) {
        $('input, textarea, select', form).each(function(){
            var el = this;
            var type = el.type;
            var tagName = el.tagName.toLowerCase()
            var widget = $(this);
            if ((type === 'text' || type === 'password' ||
                type === 'radio' || type === 'checkbox' ||
                tagName === 'select' || tagName === 'textarea') &&
                widget.prop('name')) {
                // add to widgets
                widgets.push(widget);
                // apply event handler
                widget.change(checkStatus);
            }
        });
        if (o.check) {
            checkStatus();
        }
    }

    return this.each(function(){
        if ($(o.target).length !== 0) {
            // only process if traget exists
            var form = $(this);
            setUpWidgets(form);
        }
    });
};
})(jQuery);
