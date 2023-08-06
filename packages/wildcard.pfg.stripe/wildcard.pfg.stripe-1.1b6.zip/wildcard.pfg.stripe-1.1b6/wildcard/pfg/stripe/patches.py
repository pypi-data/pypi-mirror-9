import string
from zope.contenttype import guess_content_type
from ZPublisher.HTTPRequest import FileUpload
from Products.Archetypes.interfaces.field import IField
from Products.CMFPlone.utils import safe_hasattr
from Products.CMFCore.Expression import getExprContext
from wildcard.pfg.stripe.interfaces import IStripeField
import requests
import logging
from types import StringTypes

logger = logging.getLogger('wildcard.pfg.stripe')

valid_chars = "_%s" % string.ascii_letters


def convert(val):
    try:
        return val.fCommonZ()
    except:
        if type(val) in (list, tuple):
            return ', '.join(val)
        try:
            return str(val)
        except:
            return repr(val)


def getData(obj, fields, req):
    data = {}
    for f in fields:
        fieldname = f.__name__
        showFields = getattr(obj, 'showFields', [])
        if showFields and f.id not in showFields:
            continue
        if f.isFileField():
            file = req.form.get('%s_file' % f.fgField.getName())
            if isinstance(file, FileUpload) and file.filename != '':
                file.seek(0)
                fdata = file.read()
                filename = file.filename
                mimetype, enc = guess_content_type(filename, fdata, None)
                if mimetype.find('text/') >= 0:
                    # convert to native eols
                    fdata = fdata.replace('\x0d\x0a', '\n').replace(
                        '\x0a', '\n').replace('\x0d', '\n')
                    data[fieldname] = '%s:%s:%s:%s' % (filename, mimetype,
                                                       enc, fdata)
                else:
                    data[fieldname] = '%s:%s:%s:Binary upload discarded' % (
                        filename, mimetype, enc)
            else:
                data[fieldname] = 'NO UPLOAD'
        elif not f.isLabel():
            val = req.form.get(f.fgField.getName(), '')
            if not type(val) in StringTypes:
                # Zope has marshalled the field into
                # something other than a string
                data[fieldname] = str(val)
            elif type(val) == dict:
                data.update(val)
            else:
                data[fieldname] = convert(val)

    return data


def fgProcessActionAdapters(self, errors, fields=None, REQUEST=None):
    if fields is None:
        fields = [fo for fo in self._getFieldObjects()
                  if not IField.providedBy(fo)]

    if not errors:
        if self.getRawAfterValidationOverride():
            # evaluate the override.
            # In case we end up traversing to a template,
            # we need to make sure we don't clobber
            # the expression context.
            self.getAfterValidationOverride()
            self.cleanExpressionContext(request=self.REQUEST)

        # get a list of adapters with no duplicates, retaining order
        adapters = []
        for adapter in self.getRawActionAdapter():
            if adapter not in adapters:
                adapters.append(adapter)

        for adapter in adapters:
            actionAdapter = getattr(self.aq_explicit, adapter, None)
            if actionAdapter is None:
                logger.warn(
                    "Designated action adapter '%s' is missing; ignored. "
                    "Removing it from active list." %
                    adapter)
                self.toggleActionActive(adapter)
            else:
                # Now, see if we should execute it.
                # Check to see if execCondition exists and has contents
                if safe_hasattr(actionAdapter, 'execCondition') and \
                        len(actionAdapter.getRawExecCondition()):
                    # evaluate the execCondition.
                    # create a context for expression evaluation
                    context = getExprContext(self, actionAdapter)
                    doit = actionAdapter.getExecCondition(
                        expression_context=context)
                else:
                    # no reason not to go ahead
                    doit = True

                if doit:
                    result = actionAdapter.onSuccess(fields,
                                                     REQUEST=REQUEST)
                    if type(result) is type({}) and len(result):  # noqa
                        # return the dict, which hopefully uses
                        # field ids or FORM_ERROR_MARKER for keys
                        return result

        try:
            data = getData(self, fields, REQUEST)
        except:
            logger.info('could not collect stripe metadata')
            data = {}
        # see if there is a stripe field
        fields = [fo for fo in self._getFieldObjects()
                  if IStripeField.providedBy(fo)]

        for field in fields:
            name = field.fgField.getName()
            value = REQUEST.form[name]
            params = {
                'amount': value['amount'],
                'currency': field.getStripeCurrency(),
                'source': value['token'],
                'receipt_email': value['charge_data'].get('email')
            }
            mdata_fields = field.getStripeMetadata()
            if mdata_fields and type(mdata_fields) in (list, tuple, set):
                mcount = 0
                for key in mdata_fields:
                    if key in data:
                        value = data[key]
                        if not value:
                            continue
                        mcount += 1
                        if mcount >= 10:
                            break
                        # size limits here too
                        key = "metadata[%s]" % (
                            ''.join(c for c in key if c in valid_chars))
                        params[key] = value[:200]
            resp = requests.post(
                'https://api.stripe.com/v1/charges',
                auth=(field.getStripeSecretKey(), ''),
                data=params
            )
            try:
                data = resp.json()
                if 'error' in data:
                    errors[name] = 'Stripe API Errror: %s' % (
                        data['error']['message'])
            except:
                errors[name] = 'Error processing charge'
    return errors
