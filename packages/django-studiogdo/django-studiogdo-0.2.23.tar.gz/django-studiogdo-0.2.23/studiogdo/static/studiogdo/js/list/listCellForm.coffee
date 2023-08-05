define ->

  class ListeEditForm
    
    # value = span containing the value, form = edit form
    constructor: (@list, @value, @form) ->

      # stores input elements
      @inputs = @form.querySelectorAll("input")
      @selects = @form.querySelectorAll("select")
      
      # opens edition
      @editionMode = true
      @showForm()

    commit: (evt, list) =>
      alert('edition committing to be done')

    cancel: (evt, list) =>
      list.editForm = null

    commitChange: (evt) =>
      return if !@editionMode
      evt?.preventDefault()
      @close()

      # commits only on change
      if @changed() then @commit(evt, @list) else @cancel(evt, @list)
  
    cancelChange: (evt) =>
      evt?.preventDefault()
      @close()
      @cancel(evt, @list)
      
    # checks if an edited value has changed
    changed: =>
      for input in @inputs
        return true if (input.type == "checkbox")
        new_value = input.value
        old_value = input.getAttribute("value")
        return true if (new_value != old_value)
        
      for select in @selects
        new_value = select.value
        old_value = select.getAttribute("value")
        return true if (new_value != old_value)

      return false
  
    # adds event listener for edition
    addEventListenerOnInputs: =>
      for input in @inputs
        if (input.type == "checkbox")
          input.addEventListener("click", @commitChange)
          input.addEventListener("keydown", @enter)
        else
          input.addEventListener("blur", @commitChange)
          input.addEventListener("keydown", @enter)
        
      for select in @selects
        select.addEventListener("change", @commitChange)
        select.addEventListener("keydown", @enter)

      @form.addEventListener("submit", @commitChange)
  
    # removes event listener for edition
    removeEventListenerOnInputs: =>
      for input in @inputs
        if (input.type == "checkbox")
          input.removeEventListener("click", @commitChange)
          input.removeEventListener("keydown", @enter)
        else
          input.removeEventListener("blur", @commitChange)
          input.removeEventListener("keydown", @enter)
        
      for select in @selects
        select.removeEventListener("change", @commitChange)
        select.removeEventListener("keydown", @enter)

      @form.removeEventListener("submit", @commitChange)

    enter: (evt) =>
      if (evt.keyCode == 27)
        evt.preventDefault()
        @cancelChange()
  
    # selects first input (may have several inputs)
    firstFocus: =>
      input = @form.querySelector("input")
      if (input)
        input.focus()
        input.select() if input.type != "checkbox"
        
    # closes edition
    close: =>
      @hideForm()
      @editionMode = false
        
    # shows form (hides value)
    showForm: =>
      addClassName(@value, 'hidden')
      removeClassName(@form, 'hidden')
      @addEventListenerOnInputs()

    # hides the edit form
    hideForm: =>
      @removeEventListenerOnInputs()
      removeClassName(@value, 'hidden')
      addClassName(@form, 'hidden')

