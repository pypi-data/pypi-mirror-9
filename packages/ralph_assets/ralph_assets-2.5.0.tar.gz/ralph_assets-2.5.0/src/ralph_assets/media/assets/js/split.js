$(document).ready(function () {
    var FORM_COUNT = parseInt($('input[name="form-TOTAL_FORMS"]').val());

    $('.add_row').on("click", function () {
        var old_last = $('.form-split tbody tr').last();
        if ($($('input:hidden', old_last)[2]).val() || !old_last.length) {
            var row_html = $('#row-to-copy').html();
            $('.form-split tbody').append(row_html)
            change_form_counter('add');
            renumber_forms();
            var new_last = $('.form-split tbody tr').last();
            bas = BobAjaxSelect.getInstance();
            bas.register_in_element(new_last);
            $('.results_on_deck', new_last).bind('added', function() {
                var id = $($('input:hidden', new_last)[1])
                if (id.val() == 0) {
                    id.val('')
                }
            })
            return false;
        }
    });

    $("body").delegate(".form-split .delete_row", "click", function () {
        var row_count = $('.form-split tbody tr').length;
        $(this).parents('tr').remove();
        change_form_counter('subtract');
        renumber_forms();
        return false;
    });

    function change_form_counter(action) {
        if (action == 'add') {
            FORM_COUNT += 1;
        } else if (action == 'subtract') {
            FORM_COUNT -= 1;
        }
        $('input[name="form-TOTAL_FORMS"]').val(FORM_COUNT);
    }

    function renumber_forms() {
        var form = $('.form-split tr');
        var new_fields_counter = 0
        form.each(function (i, elem) {
            $(elem).find('input, select, span, div,').each(function (j, elem) {
                var numberPattern = /\d+/g;
                var name = $(elem).attr('name');
                if (name) {
                    $(elem).attr('name', name.replace(numberPattern, i - 1));
                }
                var id = $(elem).attr('id');
                if (id) {
                    $(elem).attr('id', id.replace(numberPattern, i - 1));
                }
            });
            var id = $($(elem).find('input')[1]);
            if (id && id.val() == 0) {
                new_fields_counter++;
            }
        });
        $('input[name="form-INITIAL_FORMS"]').val(FORM_COUNT - new_fields_counter);
        $('.ordinal').each(function (i, elem) {
            $(elem).html(i + 1);
        });
    }
});
