import requests
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Registry import registerWidget


class StripeWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro': "stripewidget",
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        fieldName = field.getName()
        token = form.get('%s-stripe-token' % fieldName)

        # check on token with api...
        resp = requests.get(
            'https://api.stripe.com/v1/tokens/%s' % token,
            auth=(field.stripeSecretKey, ''),
        )
        try:
            data = resp.json()
        except:
            data = None

        data = {
            'original-amount': form.get(
                '%s-stripe-original-amount' % fieldName),
            'amount': form.get('%s-stripe-amount' % fieldName),
            'token': token,
            'charge_data': data
        }

        # also save the data back to the request so PFG can use it
        form[field.getName()] = data
        return [data]

registerWidget(StripeWidget,
               title='Stripe',
               description=(''),
               used_for=('Products.Archetypes.Field.ObjectField',)
               )
