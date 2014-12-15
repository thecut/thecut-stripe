function stripeResponseHandler(status, response) {

    'use strict';

    var $cardForm = jQuery('[name="stripe_token"]').closest('form');

    if (response.error) {
        alert(response.error.message);  // TODO: Show the errors on the form?
        $cardForm.find('[type="submit"]').prop('disabled', false);
    } else {
        $cardForm.find('[name="stripe_token"]').val(response.id);
        $cardForm.get(0).submit();
    }

}


jQuery(document).ready(function ($) {

    'use strict';

    Stripe.setPublishableKey($('[name="stripe_token"]').attr('data-stripe-publishable-key'));

    var $cardForm = $('[name="stripe_token"]').closest('form');

    $cardForm.submit(function (event) {
        event.preventDefault();
        var $form = $(this);
        $form.find('[type="submit"]').prop('disabled', true);
        Stripe.card.createToken($form, stripeResponseHandler);
        // Prevent the form from submitting with the default action
        return false;
    });

});
