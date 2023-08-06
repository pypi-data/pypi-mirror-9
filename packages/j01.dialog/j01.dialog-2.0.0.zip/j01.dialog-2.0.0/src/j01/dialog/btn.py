##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""

import zope.interface
import zope.i18nmessageid

from j01.jsonrpc import btn

_ = zope.i18nmessageid.MessageFactory('p01')


class DialogButton(btn.JSONRPCButton):
    """JSON-RPC button.

    This button requires the following javascript files:

    - jquery.js >= 1.7.0
    - j01.proxy.js
    - j01.dialog.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    """

    typ = 'DialogButton'
    method = 'j01DialogFormProcessor'
    onSuccess = 'j01DialogRenderContentSuccess'
    onError = 'j01DialogRenderContentError'
    urlGetter = None

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code"""
        # replace dots in id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('keypress', 'input', function(){
                if(!e){e = window.event;}
                key = e.which ? e.which : e.keyCode;
                if (key == 13) {
                    var data = $('#%(form)s').j01FormToArray('%(handler)s');
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s(data);
                    return false;
                }
            });
            """ % {'form': form.id.replace('.', '\\\.'),
                   'url': self.getURL(form, request),
                   'handler': self.__name__,
                   'method': self.method,
                   'arguments': self.getMethodArguments(request),
                   }

    def getJavaScript(self, action, request):
        # replace dots in id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('click', '#%(action)s', function(){
                var $btn = $('#%(action)s');
                if (!$btn.prop('disabled')) {%(trigger)s
                    var data = $('#%(form)s').j01FormToArray('%(handler)s');
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s(data);
                }
                return false;
            });
            """ % {'form': action.form.id.replace('.', '\\\.'),
                   'url': self.getURL(action.form, request),
                   'action': action.id,
                   'handler': self.__name__,
                   'trigger': self.getTrigger(action),
                   'method': self.method,
                   'arguments': self.getMethodArguments(request),
                   }


class DialogContentButton(btn.JSONRPCContentButton):
    """Dialog content button

    This button will load and render content into an existing dialog via
    JSON-RPC.

    This button requires the following javascript files:

    - jquery.js
    - j01.proxy.js
    - j01.dialog.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    """

    typ = 'DialogContentButton'
    method = 'j01DialogContent'
    onSuccess = 'j01DialogRenderContentSuccess'
    onError = 'j01DialogRenderContentError'

    def __init__(self, *args, **kwargs):
        # Provide a dialogURLGetter method
        if 'urlGetter' not in kwargs:
            raise ValueError("Must define a urlGetter methode.")
        super(DialogContentButton, self).__init__(*args, **kwargs)

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        # replace dotted id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('keypress', 'input', function(){
                if(!e){e = window.event;}
                key = e.which ? e.which : e.keyCode;
                if (key == 13) {
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s();
                    return false;
                }
            });
            """ % {'form': form.id.replace('.', '\\\.'),
                   'url': self.getURL(form, request),
                   'method': self.method,
                   'arguments': self.getMethodArguments(request),
                   }

    def getJavaScript(self, action, request):
        """Returns the button javascript code"""
        # replace dotted id with '\\.' See jquery.com for details
        return """
            $('#%(form)s').on('click', '#%(action)s', function(){
                var $btn = $('#%(action)s');
                if (!$btn.prop('disabled')) {%(trigger)s
                    proxy = getJSONRPCProxy('%(url)s');
                    proxy.addMethod(%(arguments)s);
                    proxy.%(method)s();
                }
                return false;
            });
            """ % {'form': action.form.id.replace('.', '\\\.'),
                   'action': action.id,
                   'trigger': self.getTrigger(action),
                   'method': self.method,
                   'url': self.getURL(action.form, request),
                   'arguments': self.getMethodArguments(request),
                   }


class ShowDialogButton(btn.JSButton):
    """Show dialog button

    This button will load and render a dialog via JSON-RPC

    This button requires the following javascript files:

    - jquery.js
    - j01.proxy.js
    - j01.dialog.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    """

    typ = 'ShowDialogButton'
    urlGetter = None

    def __init__(self, *args, **kwargs):
        # apply optional urlGetter
        if 'urlGetter' in kwargs:
            self.urlGetter = kwargs['urlGetter']
            del kwargs['urlGetter']
        super(ShowDialogButton, self).__init__(*args, **kwargs)

    def getData(self, action, request):
        """Returns additional data attibutes and the testing control type

        NOTE: this button data attributes are used for testing. The Browser
        located in p01.testbrowser.browser is able to handle the button clicks
        using python testing hook methods.
        """
        data = super(ShowDialogButton, self).getData(action, request)
        if request.get('paste.testing'):
            data['j01-testing-typ'] = self.typ
            data['j01-testing-url'] = self.getURL(action.form, request)
        return data

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        return """
            $('#%(form)s').on('keypress', 'input', function(event){
                if(!e){e = window.event;}
                key = e.which ? e.which : e.keyCode;
                if (key == 13) {
                    var data = $('#%(form)s').j01FormToArray('%/handler)s');
                    j01Dialog({'params': data, 'url':'%(url)s'});
                    event.preventDefault();
                    return false;
                }
            });
            """ % {
                'form': form.id.replace('.', '\\\.'),
                'handler': self.__name__,
                'url': self.getURL(form, request),
            }

    def getJavaScript(self, action, request):
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        return """
            $('#%(form)s').on('click', '#%(action)s', function(event){
                var data = $('#%(form)s').j01FormToArray('%(handler)s');
                j01Dialog({'params': data, 'url':'%(url)s'});
                event.preventDefault();
                return false;
            });
            """ % {
                'form': action.form.id.replace('.', '\\\.'),
                'action': action.id,
                'handler': self.__name__,
                'url': self.getURL(action.form, request),
            }


class DialogCloseButton(btn.JSButton):
    """Close dialog button

    This buton knows how to close the dialog and remove the dialog element
    from the html dom without access anything from the server. The javascript
    will do this without any server interaction. This means the button handler
    doesn't get called. You can also use a simple DialogButton and set
    closeDialog=True in the action handler if your server needs to get notified
    about a close dialog action.

    This button requires the following javascript files:

    - jquery.js
    - j01.proxy.js
    - j01.dialog.js

    """

    typ = 'DialogCloseButton'

    def getURL(self, form, request):
        """Returns the url based on urlGetter or the form url"""
        if self.urlGetter is not None:
            return self.urlGetter(form)

    def getData(self, action, request):
        """Returns additional data attibutes and the testing control type

        NOTE: this button data attributes are used for testing. The Browser
        located in p01.testbrowser.browser is able to handle the button clicks
        using python testing hook methods.
        """
        data = super(DialogCloseButton, self).getData(action, request)
        if request.get('paste.testing'):
            data['j01-testing-typ'] = self.typ
            data['j01-testing-expression'] = '#j01DialogHolder'
            url = self.getURL(action.form, request)
            if url is not None:
                data['j01-testing-url'] = url
        return data

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code"""
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        if url is not None:
            url = "'%s'" % url
        else:
            url = ''
        return """
            $('#%(form)s').on('keypress', 'input', function(event){
                if(!e){e = window.event;}
                key = event.which ? event.which : event.keyCode;
                if (key == 13) {
                    j01DialogClose(%s);
                    return false;
                }
            })
            """ % {
                'form': form.id.replace('.', '\\\.'),
                'url': url,
                }

    def getJavaScript(self, action, request):
        url = self.getURL(action.form, request)
        if url is not None:
            url = "'%s'" % url
        else:
            url = ''
        return """
            $('#%(form)s').on('click', '#%(action)s', function(){
                j01DialogClose(%(url)s);
            });
            """ % {
                'form': action.form.id.replace('.', '\\\.'),
                'action': action.id,
                'url': url,
                }


# default buttons
class IDialogButtons(zope.interface.Interface):

    add = DialogButton(
        title=_(u'Add')
        )

    applyChanges = DialogButton(
        title=_(u'Apply')
        )

    cancel = DialogButton(
        title=_(u'Cancel')
        )

    close = DialogCloseButton(
        title=_(u'Close')
        )

    delete = DialogButton(
        title=_(u'Delete')
        )

    confirm = DialogButton(
        title=_(u'Confirm')
        )
