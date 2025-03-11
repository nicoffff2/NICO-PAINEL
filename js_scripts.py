def js_preencher_campos():
    return """
    var texts = arguments[0];
    var simulateTab = arguments[1];
    var el = document.activeElement;
    if (el) {
        el.focus();
        el.value = texts[0];
        el.dispatchEvent(new Event('input', { bubbles:true }));
        if (simulateTab) {
            var tabEvent = new KeyboardEvent('keydown', {key:'Tab', code:'Tab', keyCode:9, which:9, bubbles:true});
            el.dispatchEvent(tabEvent);
        }
        function getNextFocusable(element) {
            var focusable = Array.prototype.slice.call(document.querySelectorAll(
                'input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])'
            ));
            var index = focusable.indexOf(element);
            if(index > -1 && index < focusable.length - 1){
                return focusable[index+1];
            }
            return null;
        }
        var next = getNextFocusable(el);
        if (next && texts.length > 1) {
            next.focus();
            next.value = texts[1];
            next.dispatchEvent(new Event('input', { bubbles:true }));
            el = next;
        }
        for(var i = 2; i < texts.length; i++){
            next = getNextFocusable(el);
            if (next) {
                next.focus();
                next.value = texts[i];
                next.dispatchEvent(new Event('input', { bubbles:true }));
                el = next;
            }
        }
    }
    """

def js_preencher_um_campo():
    return """
    var valor = arguments[0];
    var el = document.activeElement;
    if (!el || el.tagName.toLowerCase() === "body") {
         var inputs = document.querySelectorAll('input, textarea, select, a, button, [tabindex]:not([tabindex="-1"])');
         if (inputs.length > 0) {
             el = inputs[0];
         }
    }
    if (el) {
         el.focus();
         el.value = valor;
         el.dispatchEvent(new Event('input', { bubbles: true }));
    }
    """

def js_configurar_clique():
    return r"""
    document.body.addEventListener('mousedown', function(e){
        var now = Date.now();
        window.localStorage.setItem('lastClickTime', now.toString());
        window.localStorage.setItem('clickX', e.pageX.toString());
        window.localStorage.setItem('clickY', e.pageY.toString());
        window.localStorage.setItem('hackLastClickTime', now.toString());
        window.localStorage.setItem('hackClickX', e.pageX.toString());
        window.localStorage.setItem('hackClickY', e.pageY.toString());
    }, true);
    """

def js_replicate_click():
    return """
    var el = document.elementFromPoint(arguments[0], arguments[1]);
    if(el){
      if(typeof el.click === 'function')
        el.click();
      else {
        var evt = new MouseEvent('click', {bubbles: true, cancelable: true});
        el.dispatchEvent(evt);
      }
    }
    """