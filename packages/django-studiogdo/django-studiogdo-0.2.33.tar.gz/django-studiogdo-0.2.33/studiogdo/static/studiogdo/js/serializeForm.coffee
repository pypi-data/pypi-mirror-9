# Reference jQuery
$ = jQuery

# Adds plugin object to jQuery
$.fn.extend

    # Change pluginName to your plugin's name.
    serializeForm: (options) ->
        # Default settings
        settings =
            include_disabled: true

        # Merge default settings with options.
        settings = $.extend settings, options

        data = {}
        form = $(this)
        for field in form.find('input, select, textarea')
            #to include in the form:
            #a) input must not be disabled OR include_disabled option must be set
            #b) if it'a a radio, we only include the checked value
            if (!field.disabled or settings['include_disabled']) and (field.type != "radio" or field.checked)
                #if it's a checkbox, we send true or false (.checked)
                data[field.name] = switch field.type
                    when 'checkbox'
                        $(field).prop("checked")
                    when 'select-multiple'
                        ## use studiogdo field separator
                        $(field).val().join(':')
                    else
                        $(field).val()
        return data
