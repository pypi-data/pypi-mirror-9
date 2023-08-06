define ->
    
    # @filter : DOM container
    # @filter_skel : skel file
    # @mode = django (default) or html5
    # @form : DOM filter form
    
    class ListFilter
        
        constructor: (@filter, @filter_skel)->
            @mode = "django"
            
        # hide the filter
        hideFilter: =>
            return if !@filter?

            $(@filter).hide().addClass("hidden")

        # show the filter (set all to true for all content)
        showFilter: (all) =>
            return if !@filter?
                            
            hide = (elt) ->
                fom_group = $(elt).closest(".form-group")
                if fom_group.length > 0
                    fom_group.hide()
                else
                    $(elt).hide()
                $(elt.label).hide()
            show = (elt) ->
                fom_group = $(elt).closest(".form-group")
                if fom_group.length > 0
                    fom_group.show()
                else
                    $(elt).show()
                $(elt.label).show()
    
            for input in $("INPUT", @form)
                if (input.getAttribute("type") == "checkbox")
                    if !all && input.getAttribute("checked") != "checked"
                        hide(input)
                    else
                        show(input) if input.id != ""
                else
                    if !all && input.value == ""
                        hide(input)
                    else
                        show(input)
         
            for select in $("select", @form)
                if !all && select.querySelectorAll("option[selected]").length == 0
                    hide(select)
                else
                    show(select)
            
            # hides all br if not all
            for br in $("br", @form)
                if all then $(br).show() else $(br).hide()
        
            # show filter once all done
            $(@filter).show().removeClass("hidden")

        # complete the filter
        drawFilter: (after) =>
            return if !@filter?

            # hide filter before completing it
            @hideFilter()

            bocall = new BOCall
            bocall.done = =>
                @drawFilterBOCallback(bocall)
                after?()
            bocall.postFacet(null, @filter_skel, @mode)
     
        drawFilterBOCallback: (bocall) =>

            # set filter content
            $(@filter).html(bocall.responseText) if bocall?
            @drawFilterCallback()
                             
        drawFilterCallback: =>

            # get menu
            form = $("form", @filter)
            return if form.length == 0
            @form = form.get(0)
            
            # set buttons handlers
            $('#plus', @filter).on "click", (evt) =>
                evt?.preventDefault()
                @showFilter(true)
            $('#moins', @filter).on "click", (evt) =>
                evt?.preventDefault()
                @resetFilter()
                @filterCallback(evt)
            $('#go', @filter).on "click", (evt) =>
                evt?.preventDefault()
                @filterCallback(evt)
            $(@form).on('submit', @filterCallback)
            $(@form).on('keypress', @onKeypress)
            
            for label in $('label') when label.htmlFor != ''
                 elem = document.getElementById(label.htmlFor)
                 elem?.label = label

            # show filter after completing it
            @showFilter()

        filterCallback: (evt) =>
            evt?.preventDefault()

            # refresh the list and then the filter
            data = new FormData(@form) if @form?
            @list?.drawList(null, data, @drawFilter)

        resetFilter: =>

            # unset all inputs
            for input in $("input", @form) when input.id != 'nbre_ligne'
                $(input).val('')

            # unselect all options and reselect first one
            for select in $("select", @form)
                for option in $("option", select).val()
                    option.selected = false
                select.querySelector("option").selected = true
    
        # filter on key enter
        onKeypress: (evt) =>
            @filterCallback(evt) if evt.which == 13
