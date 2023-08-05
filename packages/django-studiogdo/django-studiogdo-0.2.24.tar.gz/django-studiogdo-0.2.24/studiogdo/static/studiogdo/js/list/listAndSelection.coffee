define ["studiogdo/skeleton", "list/listFilter", "list/listCellForm", "list/listSelectionForm"], (Skeleton, Filter, DefaultCellForm, DefaultSelectionForm) ->
 
    # 2 div list renderer (list + selected item)
    class ListAndSelection extends Skeleton
        
        # @list : DOM list container
        # @selected : DOM selected container
        constructor: (@list, @selected, @list_skel, @selected_skel, @CellForm, @SelectionForm) ->
            @mode = "django"
            @path = null                    # path for the list
            @selectedPath = null            # path for the selected item
        
            @bDataTable = true              # list set as a datatable
        
            @sSelectionClass = "selected"   # css class of the TR selected
            @sSelectionEvent = "click"      # event for TR selection
        
            @sEditionEvent = "dblclick"     # event for TD edition
            @jCellForm = null               # the current cell edition form
            @jSelectionForm = null          # the current selection form
        
        hideList: =>
            return if !@list?

            $(@list).hide().addClass("hidden")

            # hide filter if defined
            if @filter?
                if @filter instanceof Filter
                    @filter.hideFilter()
                else
                    $(@filter).hide()

        showList: =>
            return if !@list?

            $(@list).removeClass("hidden").show()

            # show filter if defined
            if @filter?
                if @filter instanceof Filter
                    @filter.showFilter()
                else
                    $(@filter).show()

        # complete the list at specific path if defined and setting params
        drawList: (path, params, after) =>

            # set list path
            @path ?= path if path?
            path ?= @path

            # hide list before completing it
            @hideList()

            # if the list is already there (don't call BO)
            if !@list_skel?
                @drawListBOCallback()
                return
                
            # set list content
            bocall = new BOCall
            bocall.done = =>
                @drawListBOCallback(bocall)
                after?()
            bocall.postFacet(path, @list_skel, @mode, params)
        
        drawListBOCallback: (bocall) =>

            # complete list and selected content
            if bocall?
                $(@list).html(bocall.responseText)
                @drawListCallback()
            $(@selected).empty()
         
        drawListCallback: =>
            if @bDataTable
                table = $("table", @list)
                table = $("table", @list.parentNode) if table.length == 0
                table.dataTable(@fnSettings()) # will call @__drawListCallback on draw
            else 
                @__drawListCallback()
            
        __drawListCallback: (oSettings) =>
            
            # hide list before render setting (even if already done)
            @hideList()

            # set limit alert
            nbaff = @list.querySelector("#nbaff span").innerHTML if @list.querySelector("#nbaff span")?
            nbsel = @list.querySelector("#nbsel span").innerHTML if @list.querySelector("#nbsel span")?
            if (nbaff != nbsel)
                twarn = @list.querySelector("#table_limit_warn")
                twarn.innerHTML = "Attention, la limite d’affichage a été atteinte (#{nbaff} lignes maximum)" if twarn?
            
            # render lines
            for tr in $("tbody tr, tfoot tr", @list) when !$(tr).hasClass("initialized")

                # sets selection event handler (one to avoid bouncing event)
                if @sSelectionEvent? && @selected_skel?
                    $(tr).on @sSelectionEvent, (evt) =>
                        evt.preventDefault()
                        @drawSelected(null, $(evt.delegateTarget).closest("tr"))
                
                # sets edition event handler
                if @sEditionEvent?
                    for td in $("td.editable", tr)
                        $(td).one(@sEditionEvent, @inlineEditSelectedCallback) # one fo double click not click twice
            
                # sets euro columns (format content)
                for span in $("td.euro span, td span.euro", tr)
                    val = $(span).text()
                    $(span).text(numeral(val).format('0,0$'))

                # sets cent columns (format content)
                for span in $("td.cent span, td span.cent", tr)
                    val = $(span).text()/100
                    $(span).text(numeral(val).format('0,0.00$'))

                # sets date columns (format content)
                for span in $("td.date span, td span.date", tr)
                    date = moment($(span).text())
                    if date.isValid()
                            moment($(span).text()).lang()
                            $(span).text(date.format('L'))

                # sets time columns (format content)
                for span in $("td.time span, td span.time", tr)
                    date = moment($(span).text(), ['HH:mm', 'HH:mm:ss', 'hh:mm', 'hh:mm:ss'])
                    if date.isValid()
                            $(span).text(date.format('LT'))

                # sets datetime columns (format content)
                for span in $("td.datetime span, td span.datetime", tr)
                    date = moment($(span).text())
                    if date.isValid()
                            $(span).text(date.format('LLL'))

                # sets boolean columns (adds icon)
                for span in $("td.boolean span", tr)
                    $(span).hide()
                    i = $('<i></i>').appendTo($(span).parent())
                    val = $(span).text()
                    if val == 'true'
                        i.addClass("icon-ok")
                    else
                        i.addClass("icon-plus-sign")
                        
                $(tr).addClass("initialized")

            # show grid once all done
            @showList()

        # hide the selected item
        hideSelected: =>
            $(@selected).hide().addClass("hidden")
    
        # show the selected item
        showSelected: =>
            $(@selected).removeClass("hidden").show()
    
        # complete the selected item
        drawSelected: (data, tr, after) =>

            # hide selected before completing it
            @hideSelected()
            
            # create js selection form
            if !@jSelectionForm?
                if @SelectionForm?
                    @jSelectionForm = new @SelectionForm(@)
                else
                    @jSelectionForm = new DefaultSelectionForm(@)
                
            # get selection path
            tr ?= $("tr.#{@sSelectionClass}", @list)
            if tr.length > 0
                path = tr.data("apath")
                @selectLine(tr)
            else
                path = @jSelectionForm.path
                
            # call bo if path defined
            return if !path?
            @selectedPath = path
            @drawSelectedBOCall(data, after)
        
        # may be redefine if specific BOCall should be done on selection
        drawSelectedBOCall: (data, after) =>
            bocall = new BOCall

            # on error reshow selected and show error
            error = bocall.error
            bocall.error = (info) =>
                @showSelected()
                error?(info)
                
            bocall.done = =>
                @drawSelectedBOCallback(bocall)
                after?()
            bocall.postFacet(@selectedPath, @jSelectionForm.skel, @mode, data)
            
        drawSelectedBOCallback: (bocall) =>

            # checks selection holder is defined
            if !@selected?
                alert 'No selection holder defined for the list'
                return

            # hide selected before render setting (even if already done)
            @hideSelected()
            
            # reset event handler
            #
            # ICICICICICCI
            #
            # $(evt.delegateTarget).one(@sSelectionEvent, @showSelectedCallback) if evt?
        
            # sets selected content
            $(@selected).html(bocall.responseText)
            @jSelectionForm.showSelectedCallback(@selected) if @jSelectionForm?
            @drawSelectedCallback()

            
        drawSelectedCallback: =>

            # show selected once all done
            @showSelected()

        # closes the selected item
        closeSelected: =>
            # remove selected content and reloads list
            @jSelectionForm = null
            $(@selected).empty()

        
        # commit and stay on the same state (does not go back to list)
        commitSelected: (params, after) =>
            data = new FormData(@selected.querySelector("form"))
            @drawSelected(data)

        # commit the selected item and go back to list
        commitSelectedList: (params, after) =>
            data = new FormData(@selected.querySelector("form"))
            for key, value of params
                data.append(key, value)
            @drawList(@path, data, =>
                after?()
                @closeSelected()
            )
        
        # shows the edit form associated to the selected item
        inlineEditSelectedCallback: (evt) =>
            td = evt.currentTarget

            # reset edition handler
            $(td).one(@sEditionEvent, @inlineEditSelectedCallback)

            # get span
            span = td.querySelector("span")
            return if !span?
            #return if @jCellForm?

            form = td.querySelector("form")
            return if !form?

            # shows form if no content in span (cannot click on it)
            form.classList.remove("hidden") if span.innerText == ''
            
            # close previous open edition form
            @jCellForm?.close()

            # create new one
            if @CellForm?
                @jCellForm = new @CellForm(@, span, form)
            else
                @jCellForm = new DefaultCellForm(@, span, form)
                @jCellForm.firstFocus()
                @jCellForm.commit = (evt, list) =>
                    fdata = new FormData(form)
                    @drawList(@path, fdata)
                    @jCellForm = null
            
        fnSettings: =>
                "aaSorting": [ ]
                'aLengthMenu': [[10, 25, 100, 500, -1], [10, 25, 100, 500, 'Tous']]
                "bStateSave": true
                "bLengthChange" : true
                "iDisplayLength": 10
                "fnDrawCallback": @__drawListCallback
                "sDom": "Tlfrtip<'clear'>"
                "sPaginationType": "full_numbers"
                "oLanguage":
                        "sLengthMenu": "Afficher _MENU_ lignes par page",
                        "sZeroRecords": "Pas trouvé..",
                        "sInfo": "Affichage de _START_ à _END_ sur _TOTAL_ lignes",
                        "sInfoEmpty": "Affichage de 0 à 0 sur 0 lignes",
                        "sInfoFiltered": "(filtrage sur _MAX_ lignes)",
                        "sSearch" : "Rechercher"
                        "oPaginate":
                            "sFirst" : "&nbsp;&nbsp;&nbsp;"
                            "sLast" : "&nbsp;&nbsp;&nbsp;"
                            "sNext" : "&nbsp;&nbsp;&nbsp;"
                            "sPrevious" : "&nbsp;&nbsp;&nbsp;"

        # show the selected line
        selectLine: (selected_tr) =>
            if @sSelectionClass?
                for tr in $("tr", @list)
                    $(tr).removeClass(@sSelectionClass)
                $(selected_tr).addClass(@sSelectionClass)
                
        addDeleteButtons: (msg, where) =>
            ###
            Adds delete button on each line.
            Should be added after showListCallback
                showListCallback: (oSettings) =>
                super(oSettings)
                @addDeleteButtons()
            ###
            
            msg ?= "Voulez-vous réellement faire cette action?"
            where ?= "tbody tr > td:last-child"
            
            askConfirmation = (evt) =>
                evt.stopImmediatePropagation()
                evt.preventDefault() 
                if confirm "Confirmation : #{msg}"
                    tr = $(evt.delegateTarget).closest("tr")
                    @deleteCallback(tr.data("apath"))
                
            for td in @list.querySelectorAll(where) when !(td.classList.contains("dataTables_empty") || td.classList.contains("delete_button"))
                button = $('<span alt="Détruire" title="Détruire" class="glyphicon glyphicon-trash small"/>').appendTo(td)
                button.css('float', 'right')
                $(td).addClass("delete_button")
    
                button.on "click", askConfirmation
        
        # may be redefined for specific deletion
        deleteCallback: (path) =>
            bocall = new BOCall
            bocall.done = => @drawList()
            bocall.applyCommand(path, "Unplug")

        
        class BooleanEditForm extends DefaultCellForm
            constructor: ->
                super
                @firstFocus()
                
            commit: (evt, list) =>
                list.editForm = null
                td = getParentByTagName(evt.target, "TD", true)
                if !td.classList.contains("boolean")
                    super
                    return
                bo = new BOCall
                bo.done = =>
                    @value.innerHTML = bo.responseText
                input = if evt.target.tagName=='INPUT' then evt.target else evt.target.querySelector('INPUT')
                bo.appendBOParam("i_#{td.dataset.apath}", input.value)
                bo.postProp(td.dataset.apath)
    
        class CentEditForm extends DefaultCellForm
            constructor: ->
                super
                @firstFocus()
                
            commit: (evt, list) =>
                list.editForm = null
                td = getParentByTagName(evt.target, "TD", true)
                if !td.classList.contains("cent")
                    super
                    return
                bo = new BOCall
                bo.done = =>
                    @value.innerHTML = bo.responseText
                    #centToEuro(@value, @value);
                input = if evt.target.tagName=='INPUT' then evt.target else evt.target.querySelector('INPUT')
                bo.appendBOParam("i_#{td.dataset.apath}", input.value)
                bo.postProp(td.dataset.apath)
    
