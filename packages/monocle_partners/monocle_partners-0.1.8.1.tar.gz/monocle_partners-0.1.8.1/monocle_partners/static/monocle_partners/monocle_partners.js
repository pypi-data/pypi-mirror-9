$(document).ready(function() {
    $('#partners-wrap').owlCarousel({
        items: 4,
        navigation: true,
        navigationText: [
            "<i class='fa fa-angle-left fa-5x'></i>",
            "<i class='fa fa-angle-right fa-5x'></i>"
        ],
        pagination: false,
        responsive: false
    });

    //parnters switch

    $('.a_parnter').hover(
        function () {
            $(this).find('.gray').hide();
            $(this).find('.colored').show();
        },

        function () {
            $(this).find('.gray').show();
            $(this).find('.colored').hide();
        }
    );
});