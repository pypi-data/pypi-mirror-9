from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.Archetypes.atapi import Schema
from Products.Archetypes.Field import (
    StringField, LinesField, BooleanField, FixedPointField, ObjectField
)
from Products.Archetypes.Widget import (
    StringWidget, LinesWidget, BooleanWidget, DecimalWidget, MultiSelectionWidget)
from Products.ATContentTypes.content.base import registerATCT

from Products.PloneFormGen.content.fields import FGStringField
from Products.PloneFormGen.content.fieldsBase import finalizeFieldSchema
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import DisplayList
from Products.PloneFormGen.interfaces import IPloneFormGenField

from wildcard.pfg.stripe.config import PROJECTNAME
from wildcard.pfg.stripe.widget import StripeWidget
from wildcard.pfg.stripe.interfaces import IStripeField

from zope.interface import implements


class StripeField(ObjectField):
    __implements__ = (getattr(ObjectField, '__implements__', ()),)

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'stripe',
    })

    security = ClassSecurityInfo()

    def validate(self, value, instance, errors=None, REQUEST=None, **kwargs):
        if not value.get('token'):
            return 'A payment has not been processed.'
        else:
            if not value.get('charge_data'):
                return 'Error calling stripe api'
            data = value['charge_data']
            if 'error' in data:
                return 'Stripe API Error: %s' % data['error']['message']
        # if we get this far, we need to cache the data to the request
        # for easy retrieval later... Sigh, yah, weird here...
        REQUEST.environ['%s-stripe' % self.getName()] = value
        return None


registerField(StripeField, title='Stripe Field')


class FGStripeField(FGStringField):
    """ A string entry field """

    implements(IStripeField)

    security = ClassSecurityInfo()

    schema = FGStringField.schema.copy() + Schema((
        LinesField(
            'amounts',
            required=False,
            accessor="getAmounts",
            mutator="setAmounts",
            searchable=False,
            widget=LinesWidget(
                label='Available amounts',
                description='You can also provide a description of value '
                            'using the | operator. Example: 10.00|$10 small')
        ),
        BooleanField(
            'variable',
            required=False,
            default=True,
            searchable=False,
            widget=BooleanWidget(label='Allow variable amount')
        ),
        StringField(
            'variableLabel',
            required=True,
            default='Amount: $',
            searchable=False,
            widget=StringWidget(label='Label used for variable amount field')
        ),
        FixedPointField(
            'fixedPrice',
            required=False,
            default='0.00',
            searchable=False,
            widget=DecimalWidget(
                label='Fixed amount',
                description='If filled in, ignore previous 2 fields.')
        ),
        StringField(
            'stripeSecretKey',
            require=True,
            searchable=False,
            view_permission=ModifyPortalContent,
            widget=StringWidget(label='Stripe Secret Key')
        ),
        StringField(
            'stripePublishableKey',
            require=True,
            searchable=False,
            widget=StringWidget(label='Stripe Publishable Key')
        ),
        StringField(
            'stripePanelLabel',
            required=True,
            searchable=False,
            default='More info about this',
            widget=StringWidget(label='The label of the payment button in the '
                                      'Checkout form')
        ),
        StringField(
            'stripeLabel',
            required=True,
            searchable=False,
            default='Authorize Donation',
            widget=StringWidget(label='Specify the text to be shown on the '
                                      'default blue button')
        ),
        StringField(
            'stripeCurrency',
            required=True,
            searchable=False,
            default='USD',
            widget=StringWidget(label='3 letter ISO currency code')
        ),
        LinesField(
            'stripeMetadata',
            required=False,
            default=[],
            vocabulary='getPFGFields',
            multiValued=True,
            widget=MultiSelectionWidget(
                label='Metadata Fields',
                description='Select the fields that should be included as metadata. '
                            'You can only include 10 fields. Extras will be striped.'))
    ))
    schema['required'].default = True
    schema['required'].widget.visible['edit'] = 'hidden'
    schema['hidden'].widget.visible['edit'] = 'hidden'
    schema['fgDefault'].widget.visible['edit'] = 'hidden'
    schema['fgmaxlength'].widget.visible['edit'] = 'hidden'
    schema['fgsize'].widget.visible['edit'] = 'hidden'
    schema['fgStringValidator'].widget.visible['edit'] = 'hidden'

    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormStripeField'
    archetype_name = 'StripeField'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        super(FGStripeField, self).__init__(oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StripeField(
            'fg_stripe_field',
            searchable=0,
            required=0,
            write_permission=View,
            widget=StripeWidget(),
            amounts=(
                '10.00',
                '25.00',
                '50.00',
                '100.00'),
            variable=True,
            variableLabel='Amount: $',
            fixedPrice='0.00',
            stripeSecretKey='',
            stripePublishableKey='',
            stripePanelLabel='More info about this',
            stripeLabel='Authorize Donation',
            stripeCurrency='USD'
        )

    def getPFGFields(self):
        form = aq_parent(aq_inner(self))
        if form.portal_type == 'TempFolder':
            form = aq_parent(form)
        values = []
        for field in form.values():
            if (IPloneFormGenField.providedBy(field)
                    and not IStripeField.providedBy(field)):
                values.append((
                    field.getId(),
                    field.Title()))
        return DisplayList(values)

    security.declareProtected(ModifyPortalContent, 'getStripeSecretKey')
    def getStripeSecretKey(self):  # noqa
        return self.fgField.stripeSecretKey

    security.declareProtected(ModifyPortalContent, 'setStripeSecretKey')
    def setStripeSecretKey(self, value, **kw):  # noqa
        self.fgField.stripeSecretKey = value

    security.declareProtected(View, 'getAmounts')
    def getAmounts(self):  # noqa
        return self.fgField.amounts

    security.declareProtected(ModifyPortalContent, 'setAmounts')
    def setAmounts(self, value, **kw):  # noqa
        self.fgField.amounts = value
        self.amounts = value

    # yikes, I'm lazy
    for fieldName in ['variable', 'variableLabel', 'fixedPrice',
                      'stripePublishableKey', 'stripePanelLabel',
                      'stripeLabel', 'stripeCurrency']:
        upper = fieldName[0].upper() + fieldName[1:]
        exec('''
security.declareProtected(View, 'get%(upper)s')
def get%(upper)s(self):
    return getattr(self.fgField, '%(name)s', '')

security.declareProtected(ModifyPortalContent, 'set%(upper)s')
def set%(upper)s(self, value, **kw):
    self.fgField.%(name)s = value
''' % {'name': fieldName, 'upper': upper})

    def htmlValue(self, REQUEST):
        value = REQUEST.form.get(self.__name__, 'No Input')
        if type(value) != dict:
            return 'Invalid'
        if 'error' in value:
            return 'Error charging'
        if 'charge_data' not in value:
            return 'Card not charged for some reason'
        return 'Charged to %s for $%s' % (
            value['charge_data']['email'],
            value['original-amount']
        )

registerATCT(FGStripeField, PROJECTNAME)
