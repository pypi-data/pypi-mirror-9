##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: browser.py 4127 2015-01-17 17:02:55Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy

from z3c.template.template import getPageTemplate

SKIP = object()


j01_scroller_template = """
<script type="text/javascript">
  $(document).ready(function(){
    $("%(expression)s").j01Scroller({%(settings)s});
  });
</script>
"""

j01_scroller_adhoc_template = """
<script type="text/javascript">
  $("%(expression)s").j01Scroller({%(settings)s});
</script>
"""


def j01ScrollerJavaScript(data, docReady=True, template=None):
    """Scroller generator knows how to generate the javascript options."""
    if data.get('url') is None:
        raise KeyError("Missing url")

    try:
        scrollerExpression = data.pop('scrollerExpression')
    except KeyError, e:
        scrollerExpression = '#j01Scroller'

    lines = []
    append = lines.append
    for key, value in data.items():
        if key in ['callback']:
            if not value:
                # skip if empty, use default defined in JS
                pass
            else:
                append("\n    %s: %s" % (key, value))
        elif key in ['onAfterSetResult']:
            if value == False:
                append("\n    %s: false" % key)
            else:
                append("\n    %s: %s" % (key, value))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, basestring):
            append("\n    %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    settings = ','.join(lines)

    if template is None and docReady:
        # render with document ready. This is the default option and allows to
        # include the javascript in the footer. But it can't render pager
        # loaded with JSON-RPC
        template = j01_scroller_template
    elif template is None:
        # render inplace. This option must get used if the page containing the
        # pager get loaded with JSON-RPC
        template = j01_scroller_adhoc_template

    return template % ({'expression': scrollerExpression,
                        'settings': settings})


class J01Scroller(object):
    """J01Scroller base class used for JSON-RPC and browser pages.

    Note: it's important that you load more items then the content can display
    otherwise the user can't scroll and no itmes get loaded. This is fine if
    you don't have more content and will prevent implicit scrolling.

    In other words the concept is based on loading more items then the content
    area can display and will force to apply the scroller whcih is loading
    more items on scrolling.

    """

    j01ScrollerTemplate = getPageTemplate('j01Scroller')
    j01ScrollerItemsTemplate = getPageTemplate('j01ScrollerItems')

    # internals
    _j01ScrollerURL = None
    j01ScrollerTotal = 0
    j01ScrollerContext = None
    cursor = None # iterable batching data

    # implement this attributes as session properties in your page
    j01ScrollerPage = 1
    j01ScrollerPages = 0
    j01ScrollerSortName = None
    j01ScrollerSortOrder = None

    # search query support
    j01ScrollerQuery = None
    j01ScrollerSearchString = None

    # javascript template
    j01ScrollerJavaScriptTemplate = None
    # render javascript on document ready
    j01ScrollerDocumentReady = True
    # None means internal scroll function get used. Currently nanscroller,
    # mCustomScroller is supported as scroller library
    j01ScrollerType = None # None, nano or custom

    # expressions
    j01ScrollerName = 'j01Scroller'
    j01ScrollerExpression = '#j01Scroller'
    j01ScrollerResultExpression = '#j01ScrollerResult'

    # JSON-RPC method name
    j01ScrollerMethodName = 'getJ01ScrollerResult'
    j01ScrollerCallbackMethod = None # callback uses setResult by default or
                                     # global javascript method if defined

    # sizes
    j01ScrollerBatchSize = 10
    j01ScrollerOffset = 20

    # JS event handler
    j01ScrollerOnAfterSetResult = False

    # check scroller timeout in ms
    j01ScrollerTimeout = 250

    # local storage cache
    j01ScrollerCacheKey = None # take care the cache key must be unique per
                               # context or you will get wrong data from cache
                               # None means no localStorage cache get used
    j01ScrollerCacheExpireMinutes = 5

    # optional livesearch support
    j01ScrollerSearchWidgetExpression = None
    j01ScrollerMaxReSearch = 0
    j01ScrollerMinQueryLenght = 2

    @property
    def j01ScrollerConfig(self):
        return {
            'scrollerName': self.j01ScrollerName,
            'scrollerExpression': self.j01ScrollerExpression,
            'resultExpression': self.j01ScrollerResultExpression,
            'methodName': self.j01ScrollerMethodName,
            'callback': self.j01ScrollerCallbackMethod,
            'url': self.j01ScrollerURL,
            'scrollType': self.j01ScrollerType,
            # sizes
            'batchSize': self.j01ScrollerBatchSize,
            'offset': self.j01ScrollerOffset,
            'timeout': self.j01ScrollerTimeout,
            # order support
            'sortName': self.j01ScrollerSortName,
            'sortOrder': self.j01ScrollerSortOrder,
            # event handler
            'onAfterSetResult': self.j01ScrollerOnAfterSetResult,
            # cache
            'cacheKey': self.j01ScrollerCacheKey,
            'cacheExpireMinutes': self.j01ScrollerCacheExpireMinutes,
            # live search support
            'searchWidgetExpression': self.j01ScrollerSearchWidgetExpression,
            'maxReSearch': self.j01ScrollerMaxReSearch,
            'minQueryLenght': self.j01ScrollerMinQueryLenght}

    @property
    def j01ScrollerContext(self):
        return self.context

    @property
    def j01ScrollerBatchContext(self):
        return self.j01ScrollerContext

    @property
    def j01ScrollerURL(self):
        if self._j01ScrollerURL is None:
            self._j01ScrollerURL = absoluteURL(self.j01ScrollerContext, self.request)
        return self._j01ScrollerURL

    @property
    def showJ01Scroller(self):
        return self.j01ScrollerTotal > 0

    @property
    def showMoreJ01Scroller(self):
        current = self.j01ScrollerBatchSize * self.j01ScrollerPage
        return current < self.j01ScrollerTotal

    @property
    def j01ScrollerArguments(self):
        """Get new or default page batch data method arguments"""
        page = self.request.get('p', self.j01ScrollerPage)
        batchSize = self.request.get('b', self.j01ScrollerBatchSize)
        sortName = self.request.get('n', self.j01ScrollerSortName)
        sortOrder = self.request.get('o', self.j01ScrollerSortOrder)
        searchString = self.request.get('s', self.j01ScrollerSearchString)
        return page, batchSize, sortName, sortOrder, searchString

    # cursor properties
    @property
    def j01Scroller(self):
        """Setup and return scroller batch content

        Note: we setup the j01Scroller content not during update the page or
        form, we just do it right before we use them during the render call.
        This allows us to manipulate all relevant scroller attributes e.g.
        j01ScrollerPage, j01ScrollerBatchSize etc. during form processing or
        anything else happens during update call. Feel free to setup the
        scroller batch data earlier in your implementation. As you can see, by
        default, if the cursor is not None, we will skip the scroller batch
        data setup.
        """
        if self.cursor is None:
            # J01ScrollerResult already called setUpJ01ScrollerBatchData and created
            # the cursor. Just call this method for browser requests and
            # collect batch setting from request
            page, batchSize, sortName, sortOrder, searchString = \
                self.j01ScrollerArguments
            self.setUpJ01ScrollerBatchData(page, batchSize, sortName, sortOrder,
                searchString)
        return self.j01ScrollerTemplate()

    @property
    def j01ScrollerItems(self):
        """Return scroller items

        By default we only use a template which is rendering the items.
        """
        return self.j01ScrollerItemsTemplate()

    # cursor setup
    def getJ01ScrollerQuery(self, page, batchSize, sortName=None,
        sortOrder=None, searchString=None, fields=None, skipFilter=False):
        """Hook for implement queries based on batch and serach criteria"""
        return self.j01ScrollerQuery

    def getJ01ScrollerBatchData(self, page, batchSize, sortName=None,
        sortOrder=None, searchText=None, fields=None, skipFilter=False):
        # Note: This method will fit out of the box for our m01.mongo
        # getBatchData implementation. If you like to you use another concept,
        # you need to implement getBatchData or use another method which can
        # return a tuple with the following values:
        # cursor, j01ScrollerPage, j01ScrollerPages, j01ScrollerPageTotal
        # see: setUpJ01ScrollerBatchData below for more infomation
        query = self.getJ01ScrollerQuery(page, batchSize, sortName, sortOrder,
            searchText)
        return self.j01ScrollerBatchContext.getBatchData(query, page, batchSize,
            sortName, sortOrder, searchText, fields, skipFilter)

    # setup cursor
    def setUpJ01ScrollerBatchData(self, page=None, batchSize=None,
        sortName=None, sortOrder=None, searchString=None):
        """Scroller batch data setup"""
        # set scroller attributes or use defaults. You should implement this
        # attributes as session properties
        if page is not None:
            self.j01ScrollerPage = int(page)

        if batchSize is not None:
            self.j01ScrollerBatchSize = int(batchSize)

        if sortName is not None:
            self.j01ScrollerSortName = sortName

        if sortOrder:
            self.j01ScrollerSortOrder = sortOrder

        if searchString is not None:
            self.j01ScrollerSearchString = searchString

        # setup scroller batch data
        cursor, self.j01ScrollerPage, self.j01ScrollerPages, self.j01ScrollerTotal = \
            self.getJ01ScrollerBatchData(self.j01ScrollerPage,
                self.j01ScrollerBatchSize, self.j01ScrollerSortName,
                self.j01ScrollerSortOrder, self.j01ScrollerSearchString)
        self.cursor = removeSecurityProxy(cursor)

    # return cursor
    @property
    def j01ScrollerValues(self):
        """Implement your own value iterator."""
        return self.cursor

    @property
    def j01ScrollerJavaScript(self):
        if self.showJ01Scroller or self.j01ScrollerSearchWidgetExpression:
            return j01ScrollerJavaScript(self.j01ScrollerConfig,
                self.j01ScrollerDocumentReady,
                self.j01ScrollerJavaScriptTemplate)
        else:
            return u''

    def j01ScrollerUpdate(self):
        """Update additional scroller page and jsonrpc data

        This is the only shared method which get called based on a browser and
        jsonrpc request. This means you should use this method if you need to
        setup properties which you normaly whould do in a BrowserPage update
        method.

        """
        pass

    def update(self):
        self.j01ScrollerUpdate()
        try:
            # set j01Scroller value or fail without error
            self.j01ScrollerPage = int(self.request.get('j01ScrollerPage'))
        except (TypeError, ValueError), e:
            pass
        super(J01Scroller, self).update()


###############################################################################
#
# simple scroller

j01_simple_scroller_template = """
<script type="text/javascript">
  $(document).ready(function(){
    $("%(expression)s").mCustomScrollbar({%(settings)s
    });
    var j01SHeight = $("%(expression)s").height();
    $("%(expression)sFirst").click(function() {
      $("%(expression)s").mCustomScrollbar('scrollTo', 'top');
      return false;
    });
    $("%(expression)sPrevious").click(function() {
      var val = '+=' + j01SHeight
      $("%(expression)s").mCustomScrollbar('scrollTo', val);
      return false;
    });
    $("%(expression)sNext").click(function() {
      var val = '-=' + j01SHeight
      $("%(expression)s").mCustomScrollbar('scrollTo', val);
      return false;
    });
    $("%(expression)sLast").click(function() {
      $("%(expression)s").mCustomScrollbar('scrollTo', 'bottom');
      return false;
    });
  });
</script>
"""

j01_simple_scroller_adhoc_template = """
<script type="text/javascript">
  $("%(expression)s").mCustomScrollbar({%(settings)s
  });
  var j01SHeight = $("%(expression)s").height();
  $("%(expression)sFirst").click(function() {
    $("%(expression)s").mCustomScrollbar('scrollTo', 'top');
    return false;
  });
  $("%(expression)sPrevious").click(function() {
    var val = '+=' + j01SHeight
    $("%(expression)s").mCustomScrollbar('scrollTo', val);
    return false;
  });
  $("%(expression)sNext").click(function() {
    var val = '-=' + j01SHeight
    $("%(expression)s").mCustomScrollbar('scrollTo', val);
    return false;
  });
  $("%(expression)sLast").click(function() {
    $("%(expression)s").mCustomScrollbar('scrollTo', 'bottom');
    return false;
  });
</script>
"""


def getSubConfig(data):
    """Get sub config"""
    lines = []
    append = lines.append
    for key, value in data.items():
        if value == SKIP:
            continue
        if key in ['callbacks']:
            if not value:
                # skip if empty, use default defined in JS
                pass
            else:
                append("\n        %s: %s" % (key, value))
        elif value is True:
            append("\n        %s: true" % key)
        elif value is False:
            append("\n        %s: false" % key)
        elif value is None:
            append("\n        %s: null" % key)
        elif isinstance(value, int):
            append("\n        %s: %s" % (key, value))
        elif isinstance(value, basestring):
            append("\n        %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    return ','.join(lines)


def getSimpleScrollerJavaScript(data, ready=True):
    """Scroller generator knows how to generate the javascript options."""
    try:
        scrollerExpression = data.pop('scrollerExpression')
    except KeyError, e:
        scrollerExpression = '#j01Scroller'

    lines = []
    append = lines.append
    for key, value in data.items():
        if value == SKIP:
            continue
        if key in ['mouseWheel', 'scrollButtons', 'keyboard', 'advanced']:
            if not value:
                # skip if empty, use default defined in JS
                pass
            else:
                sub = getSubConfig(value)
                append("\n    %s: {%s\n    }" % (key, sub))
        elif key in ['callbacks']:
            # apply as javascript function code
            append("\n    %s: %s" % (key, value))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, basestring):
            append("\n    %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    settings = ','.join(lines)

    if ready:
        # render with document ready. This is the default option and allows to
        # include the javascript in the footer. But it can't render pager
        # loaded with JSON-RPC
        template = j01_simple_scroller_template
    else:
        # render inplace. This option must get used if the page containing the
        # pager get loaded with JSON-RPC
        template = j01_simple_scroller_adhoc_template

    return template % ({'expression': scrollerExpression,
                        'settings': settings})


class SimpleScroller(object):
    """Simple scroller based on MCustomScrollbar without jsonrpc batching

    NOTE: this implementation MUST allways return all items.
    """
    j01ScrollerTemplate = getPageTemplate('j01Scroller')

    # internals
    cursor = None
    j01ScrollerTotal = 0
    _j01ScrollerURL = None

    # setup
    j01ScrollerDocumentReady = True
    j01ScrollerExpression = '#j01Scroller'

    # sorting
    j01ScrollerSortName = None
    j01ScrollerSortOrder = -1

    # search query support
    j01ScrollerQuery = None

    # search support
    j01ScrollerSearchWidgetExpression = None

    # config
    j01ScrollerTheme = 'dark-3'
    j01ScrollerScrollbarPosition = 'inside' # or outside
    j01ScrollerScrollInertia = 100
    j01ScrollerAlwaysVisible = True
    j01ScrollerAlwaysShowScrollbar = 2
    j01ScrollerAutoHideScrollbar = SKIP
    j01ScrollerAutoExpandScrollbar = SKIP
    j01ScrollerSnapAmount = SKIP
    j01ScrollerSnapOffset = SKIP

    # sub config
    j01ScrollerMouseWheels = {'enable': True, 'preventDefault': True}
    j01ScrollerScrollButtons = {'enable': True}
    j01ScrollerKeyboards = SKIP
    j01ScrollerAdvanceds = SKIP
    j01ScrollerCallbacks = SKIP

    # shared context support
    @property
    def j01ScrollerContext(self):
        """Returns the (container) context for setup items"""
        return self.context

    @property
    def j01ScrollerURL(self):
        if self._j01ScrollerURL is None:
            self._j01ScrollerURL = absoluteURL(self.j01ScrollerContext,
                self.request)
        return self._j01ScrollerURL

    # scroller data
    def getScrollerCursor(self, sortName=None, sortOrder=None,
        searchText=None, fields=None, skipFilter=False):
        """This method must return an iterator including a count method

        Note: your method should use the sort name, sort order and search text
        if required.
        """
        # NOTE, allways make sure that the user can't use undefined
        # sortName, sortOrder. Your cursor custom getScrollerCursor method
        # must implement such a constraint !!!
        return self.j01ScrollerContext.getScrollerCursor(sortName, sortOrder,
            searchText, fields, skipFilter)

    @property
    def j01ScrollerArguments(self):
        """Get new or default page batch data method arguments"""
        sortName = self.request.get('n', self.j01ScrollerSortName)
        sortOrder = self.request.get('o', self.j01ScrollerSortOrder)
        searchString = self.request.get('s', self.j01ScrollerSearchString)
        # sortOrder
        if sortOrder == '1':
            sortOrder = 1
        else:
            sortOrder = -1
        return sortName, sortOrder, searchString

    def setUpJ01Scroller(self, sortName, sortOrder, searchString):
        """This method must set the cursor and j01ScrollerTotal counter"""
        cursor = self.getScrollerCursor(sortName, sortOrder, searchString)
        self.cursor = removeSecurityProxy(cursor)
        self.j01ScrollerTotal = self.cursor.count()

    @property
    def j01ScrollerValues(self):
        """Return the cached scroller values"""
        return self.cursor

    # scroller
    @property
    def j01Scroller(self):
        """Return scroller content (by default based on template)

        Note: we setup the j01Scroller content not during update the page,
        we just do it right before we use them during the render call. This
        allows us to manipulate all relevant scroller attributes during form
        processing or anything else happens during update call. Feel free to
        setup the scroller data earlier in your implementation. As you can see,
        by default, if the cursor is not None, we will skip the scroller data
        setup.
        """
        if self.cursor is None:
            # setup scroller cursor and total
            self.j01ScrollerSortName, self.j01ScrollerSortOrder, \
                self.j01ScrollerSearchString = self.j01ScrollerArguments
            self.setUpJ01Scroller(self.j01ScrollerSortName,
                self.j01ScrollerSortOrder, self.j01ScrollerSearchString)
        return self.j01ScrollerTemplate()

    @property
    def showJ01Scroller(self):
        return self.j01ScrollerTotal > 0

    # javascript
    @property
    def j01ScrollerConfiguration(self):
        conf = {
            # setup
            'scrollerExpression': self.j01ScrollerExpression,
            # config
            'theme': self.j01ScrollerTheme,
            'scrollbarPosition': self.j01ScrollerScrollbarPosition,
            'scrollInertia': self.j01ScrollerScrollInertia,
            'alwaysVisible': self.j01ScrollerAlwaysVisible,
            'alwaysShowScrollbar': self.j01ScrollerAlwaysShowScrollbar,
            'autoHideScrollbar': self.j01ScrollerAutoHideScrollbar,
            'autoExpandScrollbar': self.j01ScrollerAutoExpandScrollbar,
            'snapAmount': self.j01ScrollerSnapAmount,
            'snapOffset': self.j01ScrollerSnapOffset,
            }
        # sub config
        if self.j01ScrollerMouseWheels:
            conf['mouseWheel'] = self.j01ScrollerMouseWheels
        if self.j01ScrollerScrollButtons:
            conf['scrollButtons'] = self.j01ScrollerScrollButtons
        if self.j01ScrollerKeyboards:
            conf['keyboard'] = self.j01ScrollerKeyboards
        if self.j01ScrollerAdvanceds:
            conf['advanced'] = self.j01ScrollerAdvanceds
        if self.j01ScrollerCallbacks:
            conf['callbacks'] = self.j01ScrollerCallbacks
        return conf

    @property
    def j01ScrollerJavaScript(self):
        if self.showJ01Scroller or self.j01ScrollerSearchWidgetExpression:
            return getSimpleScrollerJavaScript(self.j01ScrollerConfiguration,
                self.j01ScrollerDocumentReady)
        else:
            return u''
