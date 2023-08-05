define ['list/listAndSelection'], (List) ->
  
  class SimpleList extends List
    
    constructor: (list, skel) ->
      super(list, null, skel)
      
    showListCallback: =>
      super
      @creerBtn = @list.querySelector("#creer")
      @creerBtn.addEventListener('click', @creer) if @creerBtn?
      alert 'New command (sNewCommand) not defined' if @creerBtn? && !@sNewCommand?
      
      @form = @list.querySelector("#holder")
      valider = @form.querySelector("#valider") if @form?
      valider.addEventListener('click', @valider) if valider?
      annuler = @form.querySelector("#annuler") if @form?
      annuler.addEventListener('click', @annuler) if annuler?
      @stencilHolderNom = @form.querySelector("#stencilHolderNom") if @form?
      
    creer: (evt) =>
      evt.preventDefault() if evt
      bocall = new BOCall
      bocall.done = =>
        @commandPath = bocall.commandPath
        bo = new BOCall
        bo.appendBOParam("ap1", "U3RlbmNpbEhvbGRlcg==");
        bo.done = =>
          @stencilHolderNom.innerHTML = bo.responseText
        bo.postFacet(@commandPath, "<input id=\"inputNom\" data-value=\"Nom\" name=\"s_\"/>", "dom5")
        @creerBtn.classList.add("hidden")
        @form.classList.remove("hidden")
      bocall.applyCommand(@path, @sNewCommand)

    valider: (evt) =>
      evt.preventDefault() if evt
      bocall = new BOCall
      inputNom = @form.querySelector('#inputNom')
      bocall.appendBOParam(inputNom.getAttribute('name'), inputNom.value)
      bocall.done = =>
        @creerBtn.classList.remove("hidden")
        @form.classList.add("hidden")
        @showList()
      bocall.applyCommand(@commandPath, "NextStep")

    annuler: (evt) =>
      evt.preventDefault() if evt
      bocall = new BOCall
      bocall.applyCommand(@commandPath, "Cancel")
      bocall.done = =>
        @creerBtn.classList.remove("hidden")
        @form.classList.add("hidden")
