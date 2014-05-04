$(function() {
    function edit_fn() {
        var curr_feedback = $(this).parents('.feedback');
        var text = $(curr_feedback).find('p').html();
        $(curr_feedback).find('p').hide();
        $(curr_feedback).find('p').parent().append('<textarea class="form-control">'+text+'</textarea>');
        $(this).parent().html('<button class="done btn btn-default">Done</button>'+
            '<button class="cancel btn btn-danger">Cancel</button>');

        $('.done').click(done_edit_fn);
        $('.cancel').click(cancel_edit_fn);
    }

    function place_buttons(container) {
        $(container).html('<button class="edit btn btn-default">Edit</button>'+
            '<button class="delete btn btn-danger">Delete</button>');
        $('.edit').click(edit_fn);
        $('.delete').click(delete_fn);
    }

    function done_edit_fn() {
        var curr_feedback = $(this).parents('.feedback');
        var text = $(curr_feedback).find('textarea').val();
        edit_in_datastore({
            key: $(curr_feedback).find('input[name="key"]').val(),
            content: text
        });
        $(curr_feedback).find('.feedback-content').html(text);
        $(curr_feedback).find('textarea').remove();
        $(curr_feedback).find('p').show();
        place_buttons($(this).parent());
    }

    function cancel_edit_fn() {
        var curr_feedback = $(this).parents('.feedback');
        $(curr_feedback).find('textarea').remove();
        $(curr_feedback).find('p').show();
        place_buttons($(this).parent());
    }

    function delete_fn() {
        var feedback = $(this).parents('.feedback');
        delete_from_datastore({
            key: $(feedback).find('input[name="key"]').val(),
        });
        $(feedback).remove();
    }

    $('#add').click(function() {
        var text = $('#new-feedback').val();
        add_to_datastore(text);
    });

    $('.edit').click(edit_fn);
    $('.delete').click(delete_fn);

    function add_to_datastore(text) {
        $.post("/feedback", {content: text}, function(data) {
            $(data).appendTo('#content');
            $('.edit').click(edit_fn);
            $('.delete').click(delete_fn);
        });
    }

    function edit_in_datastore(data) {
        $.ajax({
            url: "/feedback?"+$.param(data),
            type: 'PUT'
        })
    }

    function delete_from_datastore(key) {
        $.ajax({
            url: "/feedback?"+$.param(key),
            type: 'DELETE'
        })
    }

    $('.subscribe').click(function() {
        $.ajax({
            url: "/subscribe",
            type: 'PUT'
        })

        if ($(this).html() == 'Subscribe') $(this).html('Unsubscribe');
        else $(this).html('Subscribe');
    });
});

