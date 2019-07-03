/**
 * The JavaScript engine for the pUIthon
 *
 *  @author: Grayson Wen
 *  @email: wenoptics@gmail.com
 *  @date: 6/26/2019
 *
 * */

function onEngineReady() {
    puithonJS.init();
}

// Check Jquery
if( ! window.jQuery) {
    function include(filename, onload) {
        var head = document.getElementsByTagName('head')[0];
        var script = document.createElement('script');
        script.src = filename;
        script.type = 'text/javascript';
        script.onload = script.onreadystatechange = function () {
            if (script.readyState) {
                if (script.readyState === 'complete' || script.readyState === 'loaded') {
                    script.onreadystatechange = null;
                    onload();
                }
            } else {
                onload();
            }
        };
        head.appendChild(script);
    }
    // todo Localized JQuery.js
    include('https://code.jquery.com/jquery-3.4.1.slim.min.js', onEngineReady)
} else {
    // Jquery already defined
    onEngineReady();
}

var puithonJS = {
    _domEventMap: {},
    addBindEvent: function (dom, event, pyHandlerSymbol) {
        // todo Deal with dynamic loaded elements
        if (this._domEventMap[dom] === undefined) {
            this._domEventMap[dom] = [];
        }
        // todo Validate dom
        // todo Validate binding successful
        $(dom).on(event, (evt) => {
            console.log(evt);
            window[pyHandlerSymbol](dom, JSON.stringify(evt));
        });
        console.debug(`${event} event bind with ${pyHandlerSymbol} on ${dom}`);
        this._domEventMap[dom][event] = pyHandlerSymbol
    },

    /**
     * Send value to python
     *
     * @param what The message key
     * @param value
     */
    pollValue: function (what, value) {
        pyJsReturnPut(what, value);
    },

    /**
     * Execute a javascript code string then poll the return value to python
     *
     * todo Handle exceptions
     * @param what The message key
     * @param jsStr
     */
    executeThenPoll: function (what, jsStr) {
        this.pollValue(what, eval(jsStr))
    },

    setText: function (dom, text) {
        $(dom).text(text);
    },

    setDisplay: function (dom, display) {
        $(dom).css('display', display);
    },

    setHtml: function (dom, htmltext) {
        $(dom).html(htmltext);
    },

    setClass: function (dom, class_) {
        $(dom).removeClass();
        $(dom).addClass(class_);
    },
    addClass: function (dom, class_) {
        $(dom).addClass(class_);
    },
    removeClass: function (dom, class_) {
        $(dom).removeClass(class_);
    },

    setProp: function (dom, name, val) {
        $(dom).prop(name, val)
    },

    setAttr: function (dom, name, val) {
        $(dom).attr(name, val)
    },

    getValue: function (_poll_key, dom) {
        this.pollValue(_poll_key, $(dom).val())
    },

    getProp: function (_poll_key, dom, name) {
        this.pollValue(_poll_key, $(dom).prop(name))
    },

    getAttr: function (_poll_key, dom, name) {
        this.pollValue(_poll_key, $(dom).attr(name))
    },

    getText: function (_poll_key, dom) {
        this.pollValue(_poll_key, $(dom).text())
    },

    getHtml: function (_poll_key, dom) {
        this.pollValue(_poll_key, $(dom).html())
    },

    init: function () {
        this.pollValue('_event__engine_ready', true)
    }

};
