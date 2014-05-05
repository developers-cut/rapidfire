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
        $('#new-feedback').val('');
    });

    $('.edit').click(edit_fn);
    $('.delete').click(delete_fn);

    function add_to_datastore(text) {
        $.post("/feedback", {content: text}, function(data) {
            $(data).prependTo('#feedbacks');
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

// Include the UserVoice JavaScript SDK (only needed once on a page)
UserVoice = window.UserVoice||[];
(function() {
    var uv=document.createElement('script');
    uv.type='text/javascript';
    uv.async=true;
    uv.src='//widget.uservoice.com/QaWj1H4fuafZiebNmomsg.js';
    var s=document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(uv,s)
})();

//
// UserVoice Javascript SDK developer documentation:
// https://www.uservoice.com/o/javascript-sdk
//

// Set colors
UserVoice.push(['set', {
    accent_color: '#e23a39',
    trigger_color: 'white',
    trigger_background_color: '#e23a39',
    ticket_custom_fields: {
        'Product': 'Rapid Fire',
    }
}]);

// Identify the user and pass traits
// To enable, replace sample data with actual user traits and uncomment the line
UserVoice.push(['identify', {
  //email:      'john.doe@example.com', // User’s email address
  //name:       'John Doe', // User’s real name
  //created_at: 1364406966, // Unix timestamp for the date the user signed up
  //id:         123, // Optional: Unique id of the user (if set, this should not change)
  //type:       'Owner', // Optional: segment your users by type
  //account: {
  //  id:           123, // Optional: associate multiple users with a single account
  //  name:         'Acme, Co.', // Account name
  //  created_at:   1364406966, // Unix timestamp for the date the account was created
  //  monthly_rate: 9.99, // Decimal; monthly rate of the account
  //  ltv:          1495.00, // Decimal; lifetime value of the account
  //  plan:         'Enhanced' // Plan name for the account
  //}
}]);

// Add default trigger to the bottom-right corner of the window:
UserVoice.push(['addTrigger', {mode: 'contact',
                               trigger_position: 'bottom-right'}]);


// Or, use your own custom trigger:
//UserVoice.push(['addTrigger', '#id', { mode: 'contact' }]);
