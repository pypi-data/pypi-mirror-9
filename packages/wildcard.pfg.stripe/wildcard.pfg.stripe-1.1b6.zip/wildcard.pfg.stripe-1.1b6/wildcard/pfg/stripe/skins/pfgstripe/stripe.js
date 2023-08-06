/* global alert */
/* global StripeCheckout */

(function($){
'use strict';

  $(document).ready(function(){
    var $widget = $('.pfg-stripe-widget');

    var loadStripeLibrary = function(){
      var script = document.createElement('script');
      script.src = 'https://checkout.stripe.com/checkout.js';
      var head = document.getElementsByTagName('head')[0];
      head.appendChild(script);
    };

    if($widget.length > 0){
      // first, load the stripe js
      loadStripeLibrary();
      var $form = $widget.parents('form');
      $form.submit(function(e){
        if($form[0]._submit_it){
          // cut out, credit card setup successful
          $form[0]._submit_it = false; // in case we have to try again..
          return;
        }

        var $original = $('.stripe-original-amount', $widget);
        var $amount = $('.stripe-amount', $widget);
        var $token = $('.stripe-token', $widget);

        var amount = null;
        var $fixed = $('.fixed', $widget);
        if($fixed.length > 0){
          amount = $('.fixed-value', $fixed).val();
        }else{
          var $variableAmounts = $('.variable-amounts', $widget);
          if($variableAmounts.length > 0){
            var $checked = $('input:checked', $variableAmounts);
            if($checked.length === 0){
              alert('must select amount');
              e.preventDefault();
              return;
            }else{
              if($checked.val() === 'XVariable'){
                // custom amount
                amount = $('.variable-amount', $variableAmounts).val();
                if(!amount){
                  alert('You must enter an amount');
                  e.preventDefault();
                  return;
                }
              }else{
                amount = $checked.val();
              }
            }
          }else{
            amount = $('.variable-amount', $widget).val();
            if(!amount){
              alert('You must enter an amount');
              e.preventDefault();
              return;
            }
          }
        }
        var handler = StripeCheckout.configure({
          key: $widget.attr('data-stripe-key'),
          token: function(token, args) {
            $('.stripe-token', $widget).attr('value', token.id);
            // hint to actual submit form this time
            $form[0]._submit_it = true;
            $form.submit();
          }
        });

        // we need to check if there is already a charge and no change
        if($token.val() && $original.val() === amount){
          // check for feild error, if there was, re-try CC
          var $parent = $widget.parent();
          if(!$parent.hasClass('error')){
            // no change, skip out here
            return;
          }
        }

        $('.stripe-original-amount', $widget).attr('value', amount);
        amount = amount.replace('.', '').replace('$', '');
        $('.stripe-amount', $widget).attr('value', amount);

        e.preventDefault();
        handler.open({
          name: $widget.attr('data-stripe-label'),
          description: $widget.attr('data-stripe-panelLabel'),
          amount: amount
        });
      });
    }
  });
})(jQuery);
