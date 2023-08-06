define ["studiogdo/skeleton"], (Skeleton) ->

    # @filter : DOM container
    # @filter_skel : skel file
    # @mode = django (default) or html5
    # @form : DOM filter form

    class Filter extends Skeleton

        constructor: ->
            @filter = $(".filter")
            @filter_content =  @filter.find(".filter-content")

            # set buttons handlers
            @filter.find('.toggle-filter').on "click", (evt) =>
                evt?.preventDefault()
                @toggleFilter()

            @filter.find('.reset-filter').on "click", (evt) =>
                @resetFilter(evt)

            @filter.find('.search-filter').on "click", (evt) =>
                @filterGo(evt)

            $(@filter).on 'keypress', (evt) =>
                if evt.which == 13
                    @filterGo(evt)

            $(@filter). on 'submit', (evt) =>
                @filterGo(evt)

            @showFilterIfNotEmpty()

        # show the filter (set all to true for all content)
        toggleFilter: =>
            @filter_content.toggleClass("hidden")

        # show the filter (set all to true for all content)
        showFilter: =>
            @filter_content.removeClass("hidden")

        filterGo: (evt) =>
            evt?.preventDefault()
            # refresh the list and then the filter
            params = @filter.serializeForm()
            callback = => window.location.reload()
            @postEmpty(callback, params)

        resetFilter: (evt) =>
            # unset all inputs
            @filter_content.find("input, select").val("")
            @filterGo(evt)

        showFilterIfNotEmpty: =>
            not_empty_inputs = (input for input in @filter_content.find("input") when input.value.length)
            not_empty_selects = (select for select in @filter_content.find("select") when select.value.length)

            if not_empty_inputs.length or not_empty_selects.length
                @showFilter()
