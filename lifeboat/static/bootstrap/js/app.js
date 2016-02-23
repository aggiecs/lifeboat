// Focus state for append/prepend inputs
(function ($) {
    $(".solid-bar").on("focus", "input", function () {
          $(this).closest(".input-group-btn, .input-group").addClass("focus");
        }).on("blur", "input", function () {
          $(this).closest(".input-group-btn, .input-group").removeClass("focus");
        });
})(jQuery);
