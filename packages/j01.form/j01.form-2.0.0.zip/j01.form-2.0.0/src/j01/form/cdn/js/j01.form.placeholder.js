// j01.form.placeholder.js

(function($) {
$.fn.j01Placeholder = function(p) {
    p = $.extend({
        css: 'placeholder'
    }, p);

    var i = document.createElement('input');
    if ('placeholder' in i) {
        // browser supports placeholder, just skip
        return;
    }

    function isPassword(input){
        return $(input).attr('realType') == 'password';
    }

    function valueIsPlaceholder(input){
        return input.value == $(input).attr('placeholder');
    }

    function showPlaceholder(input, loading){
        // FF and IE save values when you refresh the page. If the user
        // refreshes the page with the placeholders showing they will be the
        // default values and the input fields won't be empty. Using
        // loading && valueIsPlaceholder is a hack to get around this and
        // highlight the placeholders properly on refresh.
        if (input.value === '' || (loading && valueIsPlaceholder(input))) {
            if (isPassword(input)) {
                // Must use setAttribute rather than jQuery as jQuery throws an
                // exception when changing type to maintain compatability with 
                // IE. We use our own "compatability" method by simply
                // swallowing the error.
                try {
                    input.setAttribute('type', 'text');
                } catch (e) { }
            }
            var value = $(input).attr('placeholder');
            if (value) {
                input.value = $(input).attr('placeholder');
                $(input).addClass(p.css);
            }
        }
    }

    function hidePlaceholder(input){
        if (valueIsPlaceholder(input) && $(input).hasClass(p.css)) {
            if (isPassword(input)) {
                try {
                    input.setAttribute('type', 'password');
                    // Opera loses focus when you change the type, so we have
                    // to refocus it.
                    input.focus();
                } catch (e) { }
            }
            input.value = '';
            $(input).removeClass(p.css);
        }
    }

    return this.each(function(){
        // We change the type of password fields to text so their placeholder shows.
        // We need to store somewhere that they are actually password fields so we can convert
        // back when the users types something in.
        if ($(this).attr('type') == 'password') {
            $(this).attr('realType', 'password');
        }
        showPlaceholder(this, true);
        $(this).focus(function() {
            hidePlaceholder(this);
        });
        $(this).blur(function(){
            showPlaceholder(this, false);
        });
    });
};
})(jQuery);
