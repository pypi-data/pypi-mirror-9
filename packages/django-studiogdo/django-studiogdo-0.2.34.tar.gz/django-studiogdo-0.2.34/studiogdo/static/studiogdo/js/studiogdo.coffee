
root = exports ? window


# ##
#
#  STRING
#
# ##

unless String::trim? then String::trim = -> @replace /^\s+|\s+$/g, ""

unless String::startsWith? then String::startsWith = (str) -> this.slice(0, str.length) == str

unless String::endsWith? then String::endsWith = (str) -> this.slice(-str.length) == str

unless String::toEuro? then String::toEuro = (str) -> (parseInt(this) / 100).toFixed(2)

unless String::toCent? then String::toCent = (str) -> parseInt(str) * 100

`
root.Command = function(rootAddress, menu, pochoir) {
    this.bocall = new BOCall(rootAddress);
    this.menu = menu || null;
    this.pochoir = pochoir || null;
    this.steps = new Array();
    this.currentStepIndex = 0;
    var self = this;

    this.done = function() {
        alert('command done');
    }

    this.setStep = function(index, step) {
        this.steps[index] = step;
    }

    this.getStep = function(index) {
        return this.steps[index];
    }

    this.setCurrentStep = function(index) {
        currentStepIndex = index;

        // sets current step skeleton in pochoir
        while (this.pochoir.firstChild) {
            this.pochoir.removeChild(this.pochoir.firstChild);
        }
        this.pochoir.appendChild(this.getStep(index));

        // sets menu
        var cmd = this;
        for (var i = 0; i < index; i++) {
            this.menu[i].className = "previous_step";
            this.menu[i].addEventListener("click", function() {
                var index = i;
                cmd.setCurrentStep(index);
            });
        }
        this.menu[index].className = "current_step";
        for (var i = index + 1; i < this.menu.length; i++) {
            this.menu[i].className = "next_step";
        }
    }

    this.start = function(path, command, fdata) {
        this.bocall.done = function() {
            self.path = self.bocall.commandPath;
            self.res = JSON.parse(self.bocall.responseText);
            self.done();
        }
        this.bocall.applyCommand(path, command, fdata);
    }

    this.callNextStep = function(fdata) {
        this.bocall.done = function() {
            self.res = JSON.parse(self.bocall.responseText);
            self.done();
        }
        this.bocall.applyCommand(this.path, "NextStep", fdata);
    }
}

root.convertCentEuro = function(val, bool) {
    val = parseFloat(val);
    if (bool)
        return val / 100;
    return parseInt(val * 100);  
}
 
/* cssSelector: elements to be editable
 * form: number format see: http://numeraljs.com/
 * func: function(val, bool) treatment for bo
 */ 
root.EditableNumber = function(cssSelector, form, func) {
    if (!form)
        form = '0,0.00 $';
    if (!func)
        // bool is used for 2ways function (exemple: if you want to converto to euro to cent)
        func = function(val, bool) {
            parseFloat(val)
        }
    // query all element according to cssSelector
    var elements = document.querySelectorAll(cssSelector);

    for (var i = 0 ; i < elements.length ; i++) {
        var element = elements[i];
        // hide elements
        element.style.display = 'none';
            
        // add needed doms
        var input = document.createElement('input');
        var span = document.createElement('span');
        var attr1 = document.createAttribute('type')
        attr1.value = 'text';
        input.setAttributeNode(attr1);
        input.style.display = 'none';
        
        var val = func(element.value, true);
        if (typeof(numeral) != 'undefined')
            span.innerText = numeralFormat(val, form);
        else
            span.innerText = val;

        // insert new doms after element
        element.parentNode.insertBefore(span, element.nextSibling);
        element.parentNode.insertBefore(input, element.nextSibling);
        
        // when double clicking on span, show input
        span.addEventListener('dblclick', function(evt) {
            span = evt.currentTarget;
            input = span.previousElementSibling;
             // set input value
            if (typeof(numeral) != 'undefined')
                input.value = numeralUnformat(span.innerText, form);
            else
                input.value = span.innerText;
            
            
            // toggle elements
            input.style.display = 'block';
            this.style.display = 'none';      
            
            //focus if jQuery is available
            if (window.jQuery)
                $(input).trigger('focus');
        });
        
        // update input change
        input.addEventListener('change', function(evt) {
            element = evt.currentTarget.previousElementSibling;
            element.value = func(this.value, false);  
        });
        
        // when focusing out of input, show span
        input.addEventListener('blur', function(evt) {
            input = evt.currentTarget;
            span = input.nextElementSibling;
            element = input.previousElementSibling;
            
            // set span value
            if (typeof(numeral) != 'undefined') {
                span.innerText = numeralFormat(input.value, form);
            } else 
                span.innerText = input.value;
            element.value = func(this.value, false);  
            
            // toggle elements
            span.style.display = 'block';
            this.style.display = 'none';
        });
    }
}

/*
 * xieme colonne form associé lui appliquer €
 *
 */


root.Datagrid = function(table) {
    var self = this;
    this.table = table;
    
    this.editableNumber = function(css, form, func) {
        new EditableNumber(css, form, func);
    };
    

    this.setToEuro = function(css, bocall) {
        var tds = self.table.querySelectorAll(css);
        for (var i = 0; i < tds.length; i++) {
            var span = tds[i].querySelector("span");
            var input = tds[i].querySelector("input");
            centToEuro(span, input);
            centToEuro(span, span);

            if (bocall) {
                self.editForm = null;
                function editer(evt) {
                    if (self.editForm != null)
                        return;

                    // gets elements
                    var span = event.target;
                    var td = span.parentNode;
                    var div = td.querySelector("div");
                    var input = td.querySelector("input");

                    // opens edition
                    self.editForm = new DatagridEditForm(span, div);
                    self.editForm.firstFocus();
                    self.editForm.cancel = function(evt) {
                        self.editForm = null;
                    }
                    self.editForm.commit = function() {
                        self.editForm = null;
                        var data = new FormData(div);
                        var bc = bocall.clone();
                        bc.done = function() {
                            toEuro(span, input);
                            toEuro(span, span);
                        }
                        bc.postEmpty(path, data);
                    }
                }


                span.addEventListener("dblclick", editer, false);
            }
        }
    }

    this.addDeleteButtons = function(msg, where) {
        msg = msg || "Voulez-vous réellement faire cette action?";
        where = where || "tbody tr > td:last-child";
        var tds = this.table.querySelectorAll(where);
        for (var i = 0; i < tds.length; i++) {
            var td = tds[i];
            var button = document.createElement('BUTTON');
            button.setAttribute('style', 'float: right;');
            button.innerHTML = '<img alt="Détruire" title="Détruire" src="/shared/css/images/btn_del.png"/>';
            td.appendChild(button);

            button.addEventListener("click", askConfirmation, true);
        }
        function askConfirmation(evt) {
            if (evt) {
                evt.stopImmediatePropagation();
                evt.preventDefault();
            }
            var res = confirm("Confirmation : " + msg);
            if (res) {
                var button = evt.currentTarget;
                var tr = getParentByTagName(button, "TR");
                self.doDelete(tr, evt);
            }
        }

    }

    this.doDelete = function(tr, evt) {
        alert('delete button clicked');
    }
}

// class for the edition cell in table (datagrid)
// form may be complex to edit complex structure
root.DatagridEditForm = function(span, div) {
    var self = this;
    this.span = span;
    this.div = div;
    this.editionMode = true;

    this.inputs = div.querySelectorAll("input");
    this.selects = div.querySelectorAll("select");

    // shows form (hides value)
    addClassName(this.span, 'hidden');
    removeClassName(this.div, 'hidden');

    this.commit = function() {
        alert('edition committing to be done');
    }

    this.cancel = function() {
    }

    this.commitChanges = function(evt) {
        if (!self.editionMode)
            return;
        if (evt)
            evt.preventDefault();

        // closes edition
        self.close();
        self.editionMode = false;

        // post only on change
        if (self.changed()) {
            self.commit();
        } else {
            self.cancel();
        }
    }
    // checks if an edited value has changed
    this.changed = function() {
        for (var i = 0; i < this.inputs.length; i++) {
            var input = this.inputs[i];
            if (input.type == "checkbox") {
                return true;
            } else {
                var new_value = input.value;
                var old_value = input.getAttribute("value");
                if (new_value != old_value) {
                    return true;
                }
            }
        }
        for (var i = 0; i < this.selects.length; i++) {
            var select = this.selects[i];
            var new_value = select.value;
            var old_value = select.getAttribute("value");
            if (new_value != old_value) {
                return true;
            }
        }
        return false;
    }
    // adds event listener for edition
    this.addEventListenerOnInputs = function() {
        for (var i = 0; i < self.inputs.length; i++) {
            var input = this.inputs[i];
            if (input.type == "checkbox") {
                input.addEventListener("click", self.commitChanges);
                input.addEventListener("blur", self.close);
            } else {
                input.addEventListener("blur", self.commitChanges);
                input.addEventListener("keydown", self.enter);
            }
        }
        for (var i = 0; i < self.selects.length; i++) {
            var select = this.selects[i];
            select.addEventListener("change", self.commitChanges);
        }
        self.div.addEventListener("submit", self.commitChanges);
    }
    // removes event listener for edition
    this.removeEventListenerOnInputs = function() {
        for (var i = 0; i < self.inputs.length; i++) {
            var input = this.inputs[i];
            if (input.type == "checkbox") {
                input.removeEventListener("click", self.commitChanges);
                input.removeEventListener("blur", self.close);
            } else {
                input.removeEventListener("blur", self.commitChanges);
                input.removeEventListener("keydown", self.enter);
            }
        }
        self.div.removeEventListener("submit", self.commitChanges);
    }

    this.enter = function(evt) {
        if (evt.keyCode == 27)
            evt.target.blur();
    }
    // selects first input (may have several inputs)
    this.firstFocus = function() {
        var input = div.querySelector("input");
        if (input && input.type != "checkbox") {
            input.focus();
            input.select();
        }
    }

    this.close = function() {
        self.removeEventListenerOnInputs();
        removeClassName(self.span, 'hidden');
        addClassName(self.div, 'hidden');
    }

    this.addEventListenerOnInputs();
}
`

# ##
#
#  PATH
#
# ##

root.isPathAbsolute = (path) ->
    return path && path.charAt(0) == '/'

root.getLastNamePath = (path) ->
    index = path.lastIndexOf('/')
    return path.substring(index + 1) if index >= 0
    return path

root.getPathName = (path) ->
    index = path.lastIndexOf('/')
    return '/' if index == 0
    return path.substring(0, index) if index > 0
    return ''

root.composePath = ->
    path = ""
    for p in arguments when p
        if (path.length == 0)
            path = p
        else if isPathAbsolute(p)
            path = p
        else
            continue if p == '.'
            if p.substring(0, 2) == "./"
                p = p.substring(2)
            else if path.charAt(path.length - 1) == '/'
                path += p
            else
                path += "/" + p
    return path;


# ##
#
#  DOM methods
#
# ##

# utility function to retrieve a parent from a tag name
# if (start == true) start at element otherwise start on parent
root.getParentByTagName = (element, tag, start) ->
    obj_parent = if start then element else element.parentNode
    obj_parent = obj_parent.parentNode while obj_parent? and obj_parent.tagName != tag
    return obj_parent if obj_parent?
    return false

`
// utility function to retrieve a sibling from a tag name
root.nextSiblingByTagName = function(element, tag) {
    var obj_sibling = element.nextSibling;
    while (obj_sibling) {
        if (obj_sibling.tagName === tag) {
            return obj_sibling;
        }
        obj_sibling = obj_sibling.nextSibling;
    }
    return false;
}

// utility function to insert element just after one
root.insertFirst = function(newElement, parentElement) {
    var children = parentElement.chilNodes;
    if (children && children.length > 0) {
        parentElement.insertBefore(newElement, parentElement.children[0]);
    } else {
        parentElement.appendChild(newElement);
    }
}

// utility function to insert element just after one
root.insertAfter = function(newElement, targetElement) {
    return targetElement.parentNode.insertBefore(newElement, targetElement.nextSibling);
}

root.hasClassName = function(inElement, inClassName) {
    var regExp = new RegExp('(?:^|\\s+)' + inClassName + '(?:\\s+|$)');
    return regExp.test(inElement.className);
}

root.addClassName = function(inElement, inClassName) {
    if (!hasClassName(inElement, inClassName))
        inElement.className = [inElement.className, inClassName].join(' ');
}

root.removeClassName = function(inElement, inClassName) {
    if (hasClassName(inElement, inClassName)) {
        var regExp = new RegExp('(?:^|\\s+)' + inClassName + '(?:\\s+|$)', 'g');
        var curClasses = inElement.className;
        inElement.className = curClasses.replace(regExp, ' ');
    }
}

root.htmlCheckboxSubmitOnlyOnPatch = function(event) {
    if (!event.target.checked) {
        nextSiblingByTagName(event.target, "INPUT").setAttribute("checked", "checked");
    }
}


// --------------------------------------------------------------------------
//
//  NUMBER formating functions
//
// --------------------------------------------------------------------------

// DEPRECATED!!!!
root.centToEuro = function(src, dest) {
        var val;

        val = src.tagName.toLowerCase() === "input" ? src.value : src.innerHTML;
        val = (parseInt(val) / 100).toFixed(2);
        val = val.replace('.', ',') + ' €';
        if (dest.tagName.toLowerCase() === "input") {
            return dest.value = val;
        } else {
            return dest.innerHTML = val;
        }
    };

// DEPRECATED!!!!
root.euroToCent = function(src, dest) {
        var val;

        val = src.tagName.toLowerCase() === "input" ? src.value : src.innerHTML;
        val = stripNonNumeric(val.replace(',', '.')) * 100;
        val = val.toFixed(0);
        if (dest == null) {
            return val;
        }
        if (dest.tagName.toLowerCase() === "input") {
            return dest.value = val;
        } else {
            return dest.innerHTML = val;
        }
    };

// DEPRECATED!!!!
root.toEuro = function(src, dest) {
    var val = (src.tagName.toLowerCase() == "input") ? src.value : src.innerHTML;
    val = parseInt(val).toFixed(2);
    val = val.replace('.', ',') + ' €';
    if (dest.tagName.toLowerCase() == "input") {
        dest.value = val;
    } else {
        dest.innerHTML = val;
    }
}

root.doubleToLocale = function(src, dest) {
    var val = (src.tagName.toLowerCase() == "input") ? src.value : src.innerHTML;
    val = val.replace('.', ',');
    if (dest.tagName.toLowerCase() == "input") {
        dest.value = val;
    } else {
        dest.innerHTML = val;
    }
}

root.localeToDouble = function(src, dest) {
    var val = (src.tagName.toLowerCase() == "input") ? src.value : src.innerHTML;
    val = stripNonNumeric(val.replace(',', '.'));
    if (dest.tagName.toLowerCase() == "input") {
        dest.value = val;
    } else {
        dest.innerHTML = val;
    }
}

// This function formats numbers by adding spaces
root.numberFormat = function(nStr) {
    nStr += '';
    nStr = stripNonNumeric(nStr);
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1))
    x1 = x1.replace(rgx, '$1' + ' ' + '$2');
    return x1 + x2;
}

// This function removes non-numeric characters
root.stripNonNumeric = function(str, comma) {
    str += '';
    var rgx = /^\d|\.|-$/;
    if (comma == ',') {
        rgx = /^\d|,|-$/;
    }
    var out = '';
    for (var i = 0; i < str.length; i++) {
        if (rgx.test(str.charAt(i))) {
            if (!((str.charAt(i) == '.' && out.indexOf('.') != -1) || (str.charAt(i) == '-' && out.length != 0))) {
                out += str.charAt(i);
            }
        }
    }
    return out;
}

root.setInputUnit = function(input, unit) {
    // input must be type="text"
    if (input.getAttribute('type').toLowerCase() != 'text') {
        return;
    }

    input.addEventListener('focus', removeUnit);
    input.addEventListener('blur', addUnit);

    // removesUnit on submit
    addClassName(input, 'setInputUnit');
    var form = getParentByTagName(input, 'FORM');
    if (form && !hasClassName(form, 'setInputUnit')) {
        // adds class "setInputUnit" in order to avoid duplicating listener
        addClassName(form, 'setInputUnit');

        form.addEventListener('submit', function(event) {
            console.log('test2');
            var inputs = event.currentTarget.querySelectorAll('.setInputUnit');
            for (var i = 0; i < inputs.length; i++) {
                removeUnit(inputs[i]);
            }
        });
    }

    function addUnit() {
        input.value = numberFormat(input.value) + unit;
    }

    function removeUnit() {
        input.value = stripNonNumeric(input.value);
    }

    // initialize input
    addUnit();
}

root.extractUrlParams = function() {
    var t = location.search.substring(1).split('&');
    var f = new Array();
    for (var i = 0; i < t.length; i++) {
        var x = t[i].split('=');
        f[x[0]] = x[1];
    }
    return f;
}
`

# ##
#
#   BOCALL
#
# available options :
#
#   * async
#   * acceptNoStencil
#   * backToHomeOnError
#   * saveProject
#
# ##

class root.BOCall

    @rootAddress = ""
    @loginAddress = "login.html"

    @options = {}
    @options['async'] = true
    @options['acceptNoStencil'] = false
    @options['backToLoginOnError'] = false

    @counter = 0 # internal bocall counter

    constructor :  (options) ->

        # default options
        @options = {}
        for option of BOCall.options
            @options[option] = BOCall.options[option]
        for option of options
            @options[option] = options[option]
        
        # creates ajax request
        @xhr = new XMLHttpRequest()
        @xhr.onreadystatechange = @defaultReadyStateChangeHandler
        @rootAddress = @options['rootAddress'] ? BOCall.rootAddress
        if @rootAddress.slice(-1) == '/'
            @rootAddress = @rootAddress.slice(0, -1)
        @loginAddress = @options['loginAddress'] ? BOCall.loginAddress
    
    clone: =>
        return new BOCall(@rootAddress)

    done: =>
        alert("bocall done")

    error: (infos) =>
        alert("Erreur:\n#{infos}") if infos?

    disconnected: =>
        alert("Vous avez été déconnecté.")
        document.location.href = @loginAddress

    addScripts: (scripts) => 
        for script in scripts
            src = script.src
            if src.length > 0
                head = document.getElementsByTagName('HEAD').item(0)
                s = document.createElement("script")
                s.language = "javascript"
                s.type = "text/javascript"
                s.defer = true
                s.src = src
                head.appendChild(s)
            content = script.text
            if content.length > 0
                head = document.getElementsByTagName('HEAD').item(0)
                s = document.createElement("script")
                s.language = "javascript"
                s.type = "text/javascript"
                s.defer = true
                s.text = decodeURI(content)
                head.appendChild(s)

    simpleGet: (url) =>
        @send("GET", url)

    login: (user, passwd) =>
        step1 = =>
            if @xhr.readyState == 4
                @afterSent()
                if @xhr.status == 200
                    @done(@xhr.responseText)
                else if @xhr.status == 201 || @xhr.status == 403
                    url = @rootAddress + "/j_security_check?j_username=#{user}&j_password=#{passwd}"
                    xhr2 = new XMLHttpRequest()
                    xhr2.onreadystatechange = =>
                        if xhr2.readyState == 4
                            if xhr2.status == 200
                                @done(xhr2.responseText)
                            else if xhr2.status == 503
                                @error("Service temporairement indisponible ou en maintenance.")
                            else
                                @error("connexion invalide")
                    xhr2.open('POST', url, true)
                    xhr2.send()
                else if @xhr.status == 503
                    @error("Service temporairement indisponible ou en maintenance.")
                else
                    @error("connexion invalide")

        @xhr.onreadystatechange = step1
        @send("POST", @rootAddress + "/login.gdo?j_username=#{user}&j_password=#{passwd}")

    disconnect: =>
        @xhr.onreadystatechange = (x) =>  @defaultReadyStateChangeHandler(x, @disconnected)
        @send("POST", @rootAddress + "/disconnect.gdo")

    postEmpty: (path, formData) =>
        @formData = formData ? formData
        @appendBOParam("ap", path) if path?
        @send("POST", @rootAddress + "/empty.gdo")

    postProp: (path, formData) =>
        @formData = formData ? formData
        @appendBOParam("ap", path) if path?
        @send("POST", @rootAddress + "/prop.gdo")

    postFacet: (path, skeleton, facet, formData) =>
        @_postFacet(path, skeleton, facet, formData, false)

    postFacets: (path, skeleton, facet, formData) =>
        @_postFacet(path, skeleton, facet, formData, true)

    _postFacet: (path, skeleton, facet, formData, multi = false) =>
        if !skeleton? or !facet?
            alert('paramètres incorrects pour postFacet')
            return

        call = if !multi then "/facet.gdo" else "/facets.gdo"

        @formData = formData ? formData
        @appendBOParam("ap", path) if path?
        @appendBOParam("m", skeleton)
        @appendBOParam("f", facet)
        @send("POST", @rootAddress + call)

    applyCommand: (path, command, formData) =>
        if !command?
            alert('paramètres incorrects pour applyCommand')
            return

        @xhr.onreadystatechange = (x) =>
            if @xhr.readyState == 4
                @afterSent()
                if @checkStatus()
                    @responseText = @xhr.responseText
                    if @responseText is ''
                        @error('la commande a retourné une string vide')
                    else
                        try
                            result = JSON.parse(@responseText)
                            if (result.result < 2)
                                @commandPath = result.infos[1]
                                @done(result)
                            if (result.result == 2)
                                @error(result.infos)
                        catch error
                            @error(@responseText)
        
        @formData = formData ? formData
        @appendBOParam("ap", path) if path?
        @appendBOParam("c", command)
        @send("POST", @rootAddress + "/apply.gdo")

    send: (method, url) =>
        @beforeSend()
        BOCall.counter++

        @appendBOParam("acceptNoStencil", @options['acceptNoStencil'])
        @appendBOParam("s", @options['saveProject']) if @options['saveProject']?
        
        if (method == "GET" || window.ActiveXObject)
            for param of @data
                if (url.indexOf('?') == -1)
                    url += "?" + encodeURIComponent(param) + '=' + encodeURIComponent(@data[param])
                else
                    url += '&' + encodeURIComponent(param) + '=' + encodeURIComponent(@data[param])
        else if (method == "POST")
            formData = @formData ? new FormData()
            for param of @data
                formData.append(param, @data[param])
            
        @xhr.open(method, url, @options['async'])
        @xhr.send(formData || null)

        # ping timeout
        #
        # if (BOTimer) { clearTimeout(BOTimer); } if (BOTimeout) { BOTimer =
        # setTimeout(function() { var bocall = @clone(); bocall.postPing(); },
        # BOTimeout); }
        #

    appendBOParam: (param, value) =>
        @data ?= {}
        @data[param] = value

    defaultReadyStateChangeHandler: (x, done) =>
        if @xhr.readyState == 4
            @afterSent()
            if @checkStatus()
                @responseText = @xhr.responseText
                if done?
                    done()
                else
                    @done()
            else
                @error(@xhr.responseText)

    checkStatus: =>
        if @xhr.status > 200
            if @xhr.status == 201
                @disconnected()
            else if @xhr.status == 204 # null content
                return true
            else if @xhr.status == 401
                @error("Vous n'êtes pas autorisé à accéder à ce service.")
            else if @xhr.status == 412
                return false
            else if @xhr.status == 418
                @error("Erreur 418 : #{@xhr.responseText}")
            else if @xhr.status == 500
                #@error("Erreur interne du serveur.")
                $("body").html("Erreur 500 : #{@xhr.responseText}")
            else if @xhr.status == 501
                @error("Fonctionnalité réclamée non supportée par le serveur.")
            else if @xhr.status == 502
                @error("Mauvaise réponse envoyée à un serveur intermédiaire par un autre serveur.")
            else if @xhr.status == 503
                @error("Service temporairement indisponible ou en maintenance.")
            else if @xhr.status == 504
                @error("Temps d’attente d’une réponse d’un serveur à un serveur intermédiaire écoulé.")
            else
                @error("Erreur internet: #{@xhr.status}\n#{@xhr.responseText}")
                
            @disconnected() if @options['backToLoginOnError']
                
            return false
        return true

    cancel: =>
        @abort()

    abort: =>
        @xhr.abort()
        @afterSent()

    beforeSend: =>
        $("#wait").show()

    afterSent: =>
        BOCall.counter-- if BOCall.counter > 0
            
        if (BOCall.counter == 0)
            $("#wait").hide()

    # for dev interface
    getStencils = (path) =>
        @xhr.onreadystatechange = @defaultReadyStateChangeHandler
        
        @appendBOParam("ap", path) if path?
        @send("GET", @rootAddress + "/stencils.gdo")

    getProp = (path) =>
        @xhr.onreadystatechange = @defaultReadyStateChangeHandler
        
        @appendBOParam("ap", path) if path?
        @send("GET", @rootAddress + "/prop.gdo")

    setProp: (path, value) =>
        @xhr.onreadystatechange = @defaultReadyStateChangeHandler

        @appendBOParam("ap", path) if path?
        @appendBOParam("v", value)
        @send("POST", @rootAddress + "/set.gdo")
