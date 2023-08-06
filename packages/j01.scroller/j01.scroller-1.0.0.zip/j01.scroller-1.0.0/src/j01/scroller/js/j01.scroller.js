(function($) {
$.fn.j01Scroller = function(o) {
    o = $.extend({
        resultExpression: '#j01ScrollerResult',
        scrollerName: 'j01Scroller',
        methodName: 'getJ01ScrollerResult',
        scrollType: null,
        url: '.',
        id: 'scroller',
        // timeout
        timeout: 250,
        // position
        offset: 20,
        // sizes
        batchSize: 10,
        // JS event handler
        onAfterSetResult: false,
        // order support
        sortName: false,
        sortOrder: false,
        // cache
        cacheKey: null,
        cacheExpireMinutes: 5,
        // live search support
        searchWidgetExpression: false,
        minQueryLenght: 2,
        maxReSearch: 0,
        callback: setResult,
        onError: null,
        onTimeout: null,
        isPushState: false,
    }, o || {});

    var wrapper = null;
    var scrollable = null;
    var page = 1;
    var currentSearchText = '';
    var loading = false;
    var useLocalStorage = false;
    var sName = null;
    var endScrolling = false;

    try {
        if (o.cacheKey && 'localStorage' in window && window['localStorage'] !== null) {
            useLocalStorage = true;
        }
    } catch (e) {}


    function setResult(response) {
        var content = response.content;
        var more = response.more;
        searchText = $(o.searchWidgetExpression).val();
        if (searchText && currentSearchText != searchText) {
            // search again
            if (reSearchCounter < o.maxReSearch) {
                reSearchCounter += 1;
                doLiveSearch();
            }
            loading = false;
            return false;
        }
        ele = $(o.resultExpression);
        ele.append(content);
        if (o.onAfterSetResult){
            o.onAfterSetResult(ele);
        }
        if (o.scrollType === 'nano') {
            // reinit nanoscroller
            wrapper.nanoScroller({
                preventPageScrolling: true,
                alwaysVisible: true
            });
        }
        doCacheData(content);
        // reset loader
        loading = false;
        if (!more) {
            endScrolling = true;
        }
        if (more) {
            // only reset scroller if more content is available, otherwise
            // let the scroller as is (true) which will block from processing
            // see: setUpHandler and checkScroller
            sName = false;
        }
    }

    function doLiveSearch() {
        searchText = $(o.searchWidgetExpression).val();
        // search only if serchText is given
        if (!searchText) {
            // load again from start
            page = 1;
            loading = false;
            doLoadContent();
        }
        // search only if serchText is given
        if (searchText.length < o.minQueryLenght) {
            loading = false;
            sName = false;
            return false;
        }
        // load only if not a request is pending and there is not cache
        if(!loading) {
            // reset page
            page = 1;
            loading = true;
            // set current search text
            currentSearchText = searchText;
            var proxy = getJSONRPCProxy(o.url);
            proxy.addMethod(o.methodName, o.callback, o.onError, o.onTimeout, o.isPushState, o.id);
            // we always use 1 as page value, we only need a page larger then 1
            // if we call the livesearch with a batch
            proxy[o.methodName](page, o.batchSize, o.sortName, o.sortOrder, searchText);
        }
    }

    function setUpSearchWidget() {
        if (o.searchWidgetExpression) {
            // unbind previous event handler
            $(o.searchWidgetExpression).unbind('keyup');
            // now setup live search event handler
            $(o.searchWidgetExpression).bind('keyup', function(){
                doLiveSearch();
            });
        }
    }

    // content loader with search support
    function doLoadContent() {
        // load only if not a request is pending
        if(!loading) {
            // supports search widget search string
            if (o.searchWidgetExpression) {
                searchText = $(o.searchWidgetExpression).val();
            }else {
                searchText = '';
            }
            console.log('page ' + page);
            page += 1;
            loading = true;
            currentSearchText = searchText;
            proxy = getJSONRPCProxy(o.url);
            proxy.addMethod(o.methodName, o.callback, o.onError, o.onTimeout, o.isPushState, o.id);
            proxy[o.methodName](page, o.batchSize, o.sortName, o.sortOrder, searchText);
        }
    }

    function saveData(key, value) {
        if (useLocalStorage) {
            try {
                localStorage.setItem(key, value);
            }catch(e) {}
        }
    }

    function getData(key) {
        if (useLocalStorage) {
            try {
                return localStorage.getItem(key);
            }catch(e) {}
        }
    }

    function removeData() {
        if (useLocalStorage) {
            try {
                localStorage.removeItem(key);
            }catch(e) {}
        }
    }

    function doClearData() {
        if (useLocalStorage) {
            var timestamp = Number(new Date());
            var old = localStorage.getItem(o.cacheKey + '-time');
            var diff = timestamp - old;
            diff = Math.round(diff/1000/60);
            if(diff >= o.cacheExpireMinutes) {
                localStorage.removeItem(o.cacheKey + '-time');
                localStorage.removeItem(o.cacheKey + '-page');
                localStorage.removeItem(o.cacheKey + '-content');
            }
        }
    }

    function doCacheData(content) {
        // cache data
        if (useLocalStorage) {
            var old = getData(o.cacheKey + '-content');
            if(old === null) {
                old = "";
            }
            saveData(o.cacheKey + '-content', old + content);
            saveData(o.cacheKey + '-page', page);
            var timestamp = Number(new Date());
            saveData(o.cacheKey + '-time', timestamp);
        }
    }

    function setUpData() {
        if (useLocalStorage) {
            // clear cache if expired
            doClearData();
            try {
                var content = getData(o.cacheKey + '-content');
                if(content != undefined) {
                    page = parseInt(getData(o.cacheKey + '-page'));
                    wrapper.html(content);
                    if (o.onAfterSetResult){
                        o.onAfterSetResult(wrapper);
                    }
                }
            } catch (e) {}
        }
    }

    function checkPosition() {
        // returns true if we reach the end - offset
        var wTop = wrapper.scrollTop();
        var wBottom = wTop + wrapper.height();
        var sPosition = scrollable.height() - o.offset;
        return sPosition < wBottom ;
    }

    function doEndScrolling() {
        // set scroller name as scroller if false or none, check conditions
        // and load content
        if (!sName) {
            sName = o.scrollerName;
        }
        // check position
        if (!endScrolling && sName == o.scrollerName) {
            // prevent check more till we are ready for the next check
            sName = true;
            // load scrollable
            doLoadContent();
        }

    }

    function doCheckEndScrolling() {
        // check position before calling doEndscrolling
        if (checkPosition()) {
            doEndScrolling();
        }
    }

    function setUpScroller() {
        // this will prevent page scrolling after we reach the end of the
        // content. We will prevent the event and scroll with our own code
        // The handler will check the position later and load the content
        // if there is any. Note: this method does not load content.
        wrapper.bind('mousewheel DOMMouseScroll', function(e) {
            var scrollTo = null;
            if (e.type == 'mousewheel') {
                scrollTo = (e.originalEvent.wheelDelta * -1);
            }
            else if (e.type == 'DOMMouseScroll') {
                scrollTo = 20 * e.originalEvent.detail;
            }
            if (scrollTo) {
                e.preventDefault();
                $(this).scrollTop(scrollTo + $(this).scrollTop());
            }
        });
        // apply scroll handler to wrapper
        wrapper.scroll(function(e) {
            setInterval(function() {
                doCheckEndScrolling();
            }, o.timeout);
        });
    }

    function setUpNanoScroller() {
        wrapper.nanoScroller({
            preventPageScrolling: true,
            alwaysVisible: true
        });
        wrapper.bind("scrollend", function(e){
            doEndScrolling();
        });
    }

    function setUpCustomScroller() {
        wrapper.mCustomScrollbar({
            alwaysShowScrollbar: 2,
            alwaysVisible: true,
            scrollInertia: 100,
            mouseWheel: {
                enable: true,
                preventDefault: true
            },
            theme: 'dark-3',
            scrollButtons:{
                enable: true
            },
            // advanced: { autoScrollOnFocus: 'a' },/
            callbacks: {
                onTotalScroll: function() {
                    doEndScrolling();
                },
                onTotalScrollOffset: 50
            }
        });
    }

    return this.each(function(){
        wrapper = $(this);
        scrollable = $(o.resultExpression);
        setUpSearchWidget();
        setUpData();
        if (o.scrollType === 'nano') {
            // use nanoscroller function
            setUpNanoScroller();
        } else if (o.scrollType === 'custom') {
            // use mCustomScroller function
            setUpCustomScroller();
        } else {
            // use internal scroller function
            setUpScroller();
        }
    });
};
})(jQuery);
