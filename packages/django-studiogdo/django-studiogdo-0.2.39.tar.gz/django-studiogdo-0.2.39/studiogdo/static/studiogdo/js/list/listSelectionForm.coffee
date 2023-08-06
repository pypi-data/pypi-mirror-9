define ["studiogdo/skeleton"],(Skeleton) ->

    class ListSelectionForm extends Skeleton
        
        constructor: (@list) ->
            @skel = @list.selected_skel   # usefull for creation (if same as selection)
            
        showSelectedCallback: (selected) =>
            form = selected.querySelector("form")
            @path = form.dataset.apath if form?
            
            $("#annuler", selected).on("click", @cancel)
            $('#valider', selected).on("click", @commit)
            $("#validerLibererListe", selected).on("click", @commit_release_list)
            $("#editer", selected).on("click", @lock)
            $("#liberer", selected).on("click", @unlock)
        
        cancel: (evt) => 
            evt?.preventDefault()
            @list.drawList null, null, =>
                @list.closeSelected()

        commit: (evt) =>
            evt?.preventDefault()
            @list.commitSelected()
            
        # lock the selected stencil (the button must have the $Locked path for unlocking the stencil)
        commit_release_list: (evt) =>
            evt?.preventDefault()
            if $("#liberer").length
                #unlock
                container = $(evt.delegateTarget).closest("*[data-apath]")
                map = {}
                map["s_#{container.attr('data-apath')}"]= ""
                @list.commitSelectedList(map)
            else
                @list.commitSelectedList()

        # lock the selected stencil (the button must have the $Locked path)
        lock: (evt) =>
            evt?.preventDefault()
            data = new FormData
            data.append("p_JExvY2tlZA==", "L1Nlc3Npb24vVXNlcigxKQ==")
            @list.drawSelected(data)
            
        # unlock the selected stencil (the button must have the $Locked path)
        unlock: (evt) =>
            evt?.preventDefault()
            data = new FormData
            data.append("p_JExvY2tlZA==", "")
            @list.drawSelected(data)
