/**
 * The JavaScript engine for the pUIthon
 * */
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
     * */
    pollValue: function(what, value) {
        pyJsReturnPut(what, value);
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

    getValue: function (_poll_key, dom) {
        this.pollValue(_poll_key, $(dom).val())
    }

};
