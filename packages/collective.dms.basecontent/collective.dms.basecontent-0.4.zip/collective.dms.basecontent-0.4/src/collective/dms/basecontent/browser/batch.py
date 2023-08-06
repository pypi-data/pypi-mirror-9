from five import grok
from z3c.table.interfaces import IBatchProvider
from zope.interface import Interface
import zope.publisher.interfaces.browser
import z3c.table.interfaces
from ZTUtils import make_query


class PloneBatchProvider(grok.MultiAdapter):
    grok.name('plonebatch')
    grok.implements(IBatchProvider)
    grok.adapts(
        Interface,
        zope.publisher.interfaces.browser.IBrowserRequest,
        z3c.table.interfaces.ITable)
    batchformkeys = None
    defaultBatchLinkCSS = u''
    batchLinkCSS = {'previous': u'previous',
                    'next': u'next',
                    'first': u'first',
                    'current': u'current',
                    'last': u'last'}
    batchSpacer = u'...'
    batchStartTag = u'<div class="listingBar">'
    batchEndTag = u'</div>'
    b_start_str = 'b_start'
    addNextAfterPrevious = True

    def __init__(self, context, request, table):
        self.__parent__ = context
        self.context = context
        self.request = request
        self.table = table
        self.batch = table.values

    def update(self):
        pass

    def render(self):
        self.update()
        batch = self.batch
#        if not batch.multiple_pages:
        if not (batch.sequence_length != batch.pagesize and \
                batch.sequence_length / batch.pagesize):
            return u""

        res = [self.batchStartTag]
        append = res.append
        if batch.has_previous:
            append(self.renderBatchLink(batch.previouspage,
                self.batchLinkCSS['previous'], text='&laquo;'))

        if self.addNextAfterPrevious and batch.has_next:
            append(self.renderBatchLink(batch.nextpage,
                self.batchLinkCSS['next'], text='&raquo;'))

        # Link to first
        if batch.show_link_to_first:
            append(self.renderBatchLink(1, self.batchLinkCSS['first']))
            if batch.second_page_not_in_navlist:
                append(self.batchSpacer)

        # Pagelist with links to previous pages for quick navigation
        for pagenumber in batch.previous_pages:
            append(self.renderBatchLink(pagenumber))

        # Current page
        append(self.renderCurrentBatchLink(batch.pagenumber,
            self.batchLinkCSS['current']))

        #  Pagelist with links to next pages for quick navigation
        for pagenumber in batch.next_pages:
            append(self.renderBatchLink(pagenumber))

        # Link to last
        if batch.show_link_to_last:
            if batch.before_last_page_not_in_navlist:
                append(self.batchSpacer)
            append(self.renderBatchLink(batch.lastpage,
                    self.batchLinkCSS['last']))

        if not self.addNextAfterPrevious and batch.has_next:
            append(self.renderBatchLink(batch.nextpage,
                self.batchLinkCSS['next'], text='&raquo;'))

        append(self.batchEndTag)
        return u'\n'.join(res)

    def renderCurrentBatchLink(self, pagenumber, cssClass=u''):
        return u'<span class="%s">%s</span>' % (cssClass, pagenumber)

    def renderBatchLink(self, pagenumber, cssClass=None, text=None):
        if text is None:
            text = pagenumber

        form = self.request.form
        start = max(pagenumber - 1, 0) * self.batch.pagesize
        cssClass = cssClass and \
                ' '.join([c for c in (self.defaultBatchLinkCSS, cssClass) if c]) or \
                self.defaultBatchLinkCSS
        if self.batchformkeys:
            batchlinkparams = dict([(key, form[key])
                                    for key in self.batchformkeys
                                    if key in form])
            query = make_query(batchlinkparams, {self.b_start_str: start})
            return u'<a data-query="%s"%s>%s</a>' % (
                query, cssClass and u' class="%s"' % cssClass or u'', text)
        else:
            batchlinkparams = form.copy()
            query = make_query(batchlinkparams, {self.b_start_str: start})
            url = '%s?%s' % (self.request.ACTUAL_URL, query)
            return u'<a href="%s"%s>%s</a>' % (
                    url, cssClass and u' class="%s"' % cssClass or u'', text)


class BootstrapPloneBatchProvider(PloneBatchProvider):
    grok.baseclass()
    batchLinkCSS = {'previous': u'previous',
                    'next': u'next',
                    'first': u'first',
                    'current': u'active',
                    'last': u'last'}
    batchSpacer = u'<li class="disabled"><a>&hellip;</a></li>'
    batchStartTag = u'<div class="pagination"><ul class="pager">'
    batchEndTag = u'</ul></div>'
    addNextAfterPrevious = False

    def renderBatchLink(self, pagenumber, cssClass=None, text=None):
        result = super(BootstrapPloneBatchProvider, self).renderBatchLink(
                pagenumber, u'', text)
        return u"""<li%s>%s</li>""" % (
                cssClass and u' class="%s"' % cssClass or u'', result)

    def renderCurrentBatchLink(self, pagenumber, cssClass=u''):
        return u'<li class="active"><a href="#">%s</a></li>' % pagenumber
