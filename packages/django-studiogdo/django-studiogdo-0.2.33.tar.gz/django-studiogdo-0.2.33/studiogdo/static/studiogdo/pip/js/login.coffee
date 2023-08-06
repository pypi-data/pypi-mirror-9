define ->

    class Login

        constructor: ->
            $("#password").on "keypress", @passwdKeyPress

        passwdKeyPress: (evt) =>
            which = evt.which
            shift_status = evt.shiftKey
            maj = ((which >= 65 && which <= 90) && !shift_status) || ((which >= 97 && which <= 122) && shift_status)
            if maj
                $('#password').closest('.form-group').addClass('has-warning')
                $("#alertMaj").show()
            else
                $('#password').closest('.form-group').removeClass('has-warning')
                $("#alertMaj").hide()

    new Login