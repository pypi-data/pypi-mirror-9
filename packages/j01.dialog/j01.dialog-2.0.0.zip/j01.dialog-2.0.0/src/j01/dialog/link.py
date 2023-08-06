###############################################################################
#
# Copyright (c) 2015 Projekt01 GmbH
# All Rights Reserved.
#
###############################################################################
"""Links
$Id:$
"""
__docformat__ = "reStructuredText"


###############################################################################
#
# link

LINK = """<a href="%(url)s"%(attrs)s>%(content)s</a>
"""

def getDialogLink(request, url=None, content=None, **kws):
    """Returns a clickable <a> tag supporting testing markers

    The link will open a j01 dialog using the j01Dialog javascript method
    f your project will setup an on document ready handler for the cess
    selector a.j01DialogLink

    Note: the rendered dom element is supported by p01.testbrowser testing!
    You can test this with something like:

        link = browser.getLink(text=None, url=None, id=None, index=0)
        link.click()

    Note: this link setup is different then the setup used in
    j01.jsonrpc/link.py because we load the dialog content from the server with
    a non async request. This means we don't use onSuccess and onError testing
    markers e.g. data-j01.testing-success etc.

    """
    # setup default attributes
    data = {
        'class': 'j01DialogLink',
        }
    # setup testing markers
    if request.get('paste.testing'):
        # testing
        data['data-j01-testing-typ'] = 'J01Dialog'
        data['data-j01-testing-url'] = url
    # update and override default data
    data.update(**kws)
    # render link
    aStr = ''
    for k, v in data.items():
        aStr += ' %s="%s"' % (k, v)
    return LINK % {'url': url, 'attrs': aStr, 'content': content}
