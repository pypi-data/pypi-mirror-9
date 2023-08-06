var Qe = function(node){

    var Qe = function(node){
        this.node = node;
    };

    Qe.prototype.styles = function(node) {
        node = node || this.node;
        var cssProperties = node.ownerDocument.defaultView.getComputedStyle(node);
        var propertyNames = Array.prototype.slice.call(cssProperties, 1)
        var json = {}
        Array.prototype.map.call(propertyNames, function(item){json[item] = cssProperties.getPropertyValue(item)});
        return json;
    };

    Qe.prototype.cssSelector = function (node){
        var names = [];
        while (node.parentNode){
            if (node.id){
                names.unshift('#'+node.id);
                break;
            }else{
                if (node == node.ownerDocument.documentElement) names.unshift(node.tagName);
                else{
                    for (var c = 1, e = node; e.previousElementSibling; e = e.previousElementSibling, c++);
                    names.unshift(node.tagName+":nth-child(" + c + ")");
                }
                node = node.parentNode;
            }
        }
        return names.join(" > ");
    }


    Qe.prototype.toJson = function(node){
        node = node || this.node;
        if(node instanceof HTMLElement) {
            return this._elementToJson(node);
        } else if(node instanceof HTMLCollection || node instanceof NodeList) {
            var map = Array.prototype.map;
            var that = this;
            return map.call(node, function(node){
                return that._elementToJson(node);
            });
        }
    };

    Qe.prototype._elementToJson = function(node){
        var that = this;
        var map = Array.prototype.map,
            slice = Array.prototype.slice,
            forEach = Array.prototype.forEach;

        var attributes = {};
        map.call(node.attributes, function(item){
            attributes[item.name] = item.value;
            return {'name': item.name, 'value': item.value};
        });

        var json = {
            'tag': node.tagName,
            'id': node.id,
            'classes': slice.call(node.classList),
            'attributes': attributes,
            'styles': that.styles(node),
            'selector': that.cssSelector(node),
            'html': node.outerHTML
        };

        if(node instanceof HTMLFormElement) {
            json['name'] = node.name;
            json['action'] = node.action;
            json['method'] = node.method;
            json['elements'] = this.toJson(node.elements);
        };

        if(node instanceof HTMLInputElement) {
            json['name'] = node.name;
            json['value'] = node.value;
            json['type'] = node.type;
        };

        if(node instanceof HTMLSelectElement) {
            var that = this;
            var options = [];
            forEach.call(node.options, function(item){
                var option = that._elementToJson(item);
                options.push(option)
            });
            json['options'] = options;
        };

        if(node instanceof HTMLOptionElement) {
            json['name'] = node.text;
            json['value'] = node.value;
        }

        return json;
    };


    return new Qe(node);
};

Qe.forms = function() {
    var forEach = Array.prototype.forEach;

    var documents = [window.document];
    forEach.call(window.frames, function(frame){
        try {
            if (frame.document.forms.length > 0) {
                documents.push(frame.document);
            }
        } catch (e) {
            return false;
        }
    });

    var forms = documents.map(function(document){
        return Qe(document.forms).toJson();
    });

    forms = forms.reduce(function(a, b) {
        return a.concat(b);
    });

    return forms.filter(function(form){
        return form;
    });

};

Qe.links = function(){
    var filter = Array.prototype.filter

    var links = filter.call(document.links, function(link){
        return link.hostname == document.location.hostname && link.protocol.indexOf('http') == 0
    });

    links = links.map(function(link){
        // Ignore query params link.search
        return 'http:' + '//' + link.hostname + link.pathname
    });

    links = links.filter(function(value, index, arr){
        return arr.indexOf(value) === index;
    });
    return links
};

Qe.cssRules = function(){
    var filter = Array.prototype.filter
    var map = Array.prototype.map
    var rules = map.call(document.querySelectorAll('*'), function(element){
        return element.ownerDocument.defaultView.getMatchedCSSRules(element,'');
    });

    var items = rules.map(function(list){
        list = list || [];
        return map.call(list, function(rule){
            return rule.cssText
        });
    });

    var flattened = items.reduce(function(a, b) {
        return a.concat(b);
    });

    var rules = flattened.filter(function(value, index, arr){
        return arr.indexOf(value) === index;
    });

    var sheets = filter.call(document.styleSheets, function(sheet){
        return sheet.rules;
    });

    var _rules = sheets.map(function(sheet){
        return filter.call(sheet.rules, function(rule){

            // regex for pseudo - /^[\#\.\w\ ]*\:+:?[\#\.\w\-\(\)]*[\,\{\ ]*$/
            return rule.cssText.indexOf(':hover') > -1 ||
                rule.cssText.indexOf(':active') > -1 ||
                rule.cssText.indexOf(':focus') > -1 ||
                rule.cssText.indexOf(':visited') > -1 ||
                rule.cssText.indexOf(':link') > -1 ||
                rule.cssText.indexOf(':first-child') > -1 ||
                rule.cssText.indexOf(':nth-child') > -1 ||
                rule.cssText.indexOf(':last-child') > -1 ||
                rule.cssText.indexOf(':before') > -1 ||
                rule.cssText.indexOf(':after') > -1 ||
                rule.cssText.indexOf('::before') > -1 ||
                rule.cssText.indexOf('::after') > -1 ||
                rule.cssText.indexOf(':first-line') > -1 ||
                rule.cssText.indexOf(':first-letter') > -1 ||
                rule.cssText.indexOf('::first-line') > -1 ||
                rule.cssText.indexOf('::first-letter') > -1 ||
                rule.cssText.indexOf('menu') > -1


        });
    });
    _rules = _rules.reduce(function(a, b) {
        return a.concat(b);
    });

    _rules = _rules.map(function(rule){
        return rule.cssText;
    });

    _rules.forEach(function(item){
        rules.push(item);
    });

    return rules
};

/** https://developer.mozilla.org/en-US/docs/Web/API/document.cookie **/
Qe.cookies = {
  getItem: function (sKey) {
    return decodeURIComponent(document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1")) || null;
  },
  setItem: function (sKey, sValue, vEnd, sPath, sDomain, bSecure) {
    if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) { return false; }
    var sExpires = "";
    if (vEnd) {
      switch (vEnd.constructor) {
        case Number:
          sExpires = vEnd === Infinity ? "; expires=Fri, 31 Dec 9999 23:59:59 GMT" : "; max-age=" + vEnd;
          break;
        case String:
          sExpires = "; expires=" + vEnd;
          break;
        case Date:
          sExpires = "; expires=" + vEnd.toUTCString();
          break;
      }
    }
    document.cookie = encodeURIComponent(sKey) + "=" + encodeURIComponent(sValue) + sExpires + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "") + (bSecure ? "; secure" : "");
    return true;
  },
  removeItem: function (sKey, sPath, sDomain) {
    if (!sKey || !this.hasItem(sKey)) { return false; }
    document.cookie = encodeURIComponent(sKey) + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" + ( sDomain ? "; domain=" + sDomain : "") + ( sPath ? "; path=" + sPath : "");
    return true;
  },
  hasItem: function (sKey) {
    return (new RegExp("(?:^|;\\s*)" + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=")).test(document.cookie);
  },
  keys: /* optional method: you can safely remove it! */ function () {
    var aKeys = document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, "").split(/\s*(?:\=[^;]*)?;\s*/);
    for (var nIdx = 0; nIdx < aKeys.length; nIdx++) { aKeys[nIdx] = decodeURIComponent(aKeys[nIdx]); }
    return aKeys;
  }
};

window.Qe = Qe;