/**
 * Created by sid on 03/02/2017.
 */
(function() {
    function checkDegreeTypeOther(elem) {
        elem = elem || $('#id_degree_type');
        var otherBlock = $('#field_degree_type_other');

        if (elem.val() == '') {
            otherBlock.show();
        }
        else {
            otherBlock.hide();
        }
    }

    $(document).on('change', '#id_degree_type', function() {
        checkDegreeTypeOther($(this));
    });

    // Initial check
    checkDegreeTypeOther();
})();
