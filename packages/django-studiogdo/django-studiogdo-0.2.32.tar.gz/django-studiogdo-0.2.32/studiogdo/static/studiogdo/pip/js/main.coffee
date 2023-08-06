define ->

    moment?.locale("fr");
    numeral?.language("fr")

    class Main

        constructor: ->

            # set menu active
            url = window.location.pathname
            main_menu = $("ul.nav#mainMenu")
            main_menu.find("li").removeClass('active')
            main_menu.find("a[href='#{url}']").parents("li").addClass('active')

            # sets user logged
            $("#disconnect").on "click", (evt) =>
                @disconnect()

            # listener on all node inserted (called now and on further element added)
            $("body").on "DOMNodeInserted", (evt) =>
                @for_all(evt.target)
            @for_all($("body"))

        disconnect: (evt) =>
            evt?.preventDefault()
            bocall = new BOCall
            bocall.disconnect()

        # will be executed on all node added
        for_all: (target) =>

            # unbind node insertion to avoid recursive calls
            $("body").off "DOMNodeInserted"

            # alert in case of edition, but not in edition mode
            alert_edition = (evt)->
                target = $(evt.delegateTarget)

                # does nothing if post element has class no_change
                if target.hasClass("no_change")
                    return

                # check edition mode (local vs global)
                detail = target.closest(".details-form")
                if detail.length > 0
                    panel = target.closest(".panel")

                    # show save changes form
                    if panel.find(".save-changes").length > 0
                        panel.addClass("panel-danger")
                        panel.find(".save-changes").show()

                    # alert change done witout editing mode
                    else if detail.find('#editer').length > 0
                        alert("Attention: Vous n'êtes pas en mode édition!")

            # set alert on post elements
            for post in $("input", target) when $(post).attr("name") != "" and $(post).attr("type") != "button" and $(post).attr("type") != "file"
                $(post).change alert_edition
            for post in $("textarea", target) when $(post).attr("name") != ""
                $(post).change alert_edition
            for post in $("select", target) when $(post).attr("name") != ""
                $(post).change alert_edition

            # set date time picker
            datepicker = $(".datepicker", target)
            if (datepicker.length > 0 and datepicker.find("input").size() > 0)

                # set as date picker
                # http://eonasdan.github.io/bootstrap-datetimepicker/Options/
                # http://momentjs.com/docs/#/displaying/format/
                datepicker.datetimepicker {
                    locale: 'fr'
                    format: "L"
                }

                # set min/max datepicker
                datepicker.filter(".start").on("dp.change", (e) ->
                    end = $(e.delegateTarget).closest(".form-group").parent().find(".datepicker.end")
                    end.data("DateTimePicker").setMinDate(e.date);
                )
                datepicker.filter(".end").on("dp.change", (e) ->
                    start = $(e.delegateTarget).closest(".form-group").parent().find(".datepicker.start")
                    start.data("DateTimePicker").setMaxDate(e.date)
                )

            # set toggle next button
            toggle_next = $(".toggle-next", target)
            toggle_next.on "click", (e) -> $(e.delegateTarget).next().toggle()
            toggle_next = $(".fade-toggle-next", target)
            toggle_next.on "click", (e) -> $(e.delegateTarget).next().fadeToggle()

            # rebind node insertion
            $("body").on "DOMNodeInserted", (evt) =>
                @for_all(evt.target)

