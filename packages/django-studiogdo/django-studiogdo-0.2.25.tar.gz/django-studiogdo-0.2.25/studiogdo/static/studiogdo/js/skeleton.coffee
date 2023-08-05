define ->

    class Skeleton

        constructor: (@path) ->

        ###
        #   Studiogdo API
        ###

        getBOCall: (params={}, rootAddress=null) =>
            bocall = new BOCall({"rootAddress":rootAddress})
            for k,v of params
                bocall.appendBOParam(k,v)
            return bocall

        applyCommand: (callback, path, cmd, params={}) =>
            bocall = @getBOCall(params)
            bocall.done = => callback()
            bocall.applyCommand(path, cmd)
    
        postFacet: (callback, path, skel, params={}) =>
            bocall = @getBOCall(params)
            bocall.done = => callback(bocall)
            bocall.postFacet(path, skel, 'django')

        postEmpty: (callback, params={}) =>
            bocall = @getBOCall(params)
            bocall.done = => if callback then callback() else null
            bocall.postEmpty()

