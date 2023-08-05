define ["list/listAndSelection"], (List) ->
    
    class ListOrSelection extends List

        drawSelectedCallback: =>
            @hideList()
            super
        
        closeSelected: =>
            super
            @showList()
            @hideSelected()


