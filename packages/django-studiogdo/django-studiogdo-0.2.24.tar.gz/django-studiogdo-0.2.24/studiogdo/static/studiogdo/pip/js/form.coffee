define ->

    class Form

        constructor: (@path) ->

            try
                $('.form-control.datetimepicker').datetimepicker(
                    language: 'fr'
                    format: 'DD/MM/YYYY hh:mm:ss'
                    weekStart: 1
                )
                $('.form-control.datepicker').datetimepicker(
                    language: 'fr'
                    format: 'DD/MM/YYYY'
                    weekStart: 1
                )
                $('.form-control.timepicker').datetimepicker(
                    language: 'fr'
                    format: 'hh:mm:ss'
                    weekStart: 1
                )
            catch error
                null

            $("#editer").one "click", (evt) =>
                evt?.preventDefault()
                bocall = new BOCall
                bocall.done = => window.location.reload()
                bocall.applyCommand(@path, "$Lock")

            $(".liberer").one "click", =>
                #we don't want to prevent default here
                bocall = new BOCall
                bocall.done = =>
                bocall.applyCommand(@path, "$Unlock")

            $('form').one "submit", (evt) =>
                form = $(evt.delegateTarget)
                for checkbox in form.find("[type=checkbox]")
                    if !checkbox.checked
                        form.append($('<input />').attr('type', 'hidden')
                                                  .attr('name', checkbox.name)
                                                  .attr('value', "false"))

            # s'il y a une entree hidden pour ce checkbox, on la desactive quand il est actif et vice versa
            checkboxes = $("[type=checkbox]").on "change", (evt) =>
                checkbox = $(evt.target)
                @update_hidden_checkbox(checkbox)
            for checkbox in checkboxes
                @update_hidden_checkbox($(checkbox))

        update_hidden_checkbox: (checkbox) =>
            hidden = checkbox.siblings("[type=hidden]")
            if hidden.size()
                disabled = checkbox.is(":checked")
                hidden.prop("disabled", disabled)
