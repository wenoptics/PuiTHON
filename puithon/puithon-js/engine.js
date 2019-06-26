/**
 * The JavaScript engine for the pUIthon
 * */
var puithonJS = {

    _domEventMap: {},
    addBindEvent: function (dom, event, pyHandlerSymbol) {
        if (this._domEventMap[dom] === undefined) {
            this._domEventMap[dom] = [];
        }
        // todo Validate dom
        // todo Validate binding successful
        $(dom).on(event, (evt) => {
            console.log(evt);
            window[pyHandlerSymbol](dom, JSON.stringify(evt));
        });
        console.log(`${event} event bind with ${pyHandlerSymbol} on ${dom}`);
        this._domEventMap[dom][event] = pyHandlerSymbol

    },

    setText: function (dom, text) {
        console.log(text);
        $(dom).text(text);
    }
};
