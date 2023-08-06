Commentator = ((o, $) ->
  o.init = ->

    $.ajaxSetup beforeSend: (xhr) ->
      xhr.setRequestHeader "X-CSRFToken", Commentator.utils.getCookie("csrftoken")
      return

    unless typeof window["prettyPrint"] is "function"
      document.write "<script src=\"" + CommentatorConfig.staticUrl + "commentator/js/lib/prettify/prettify.js\"></script>"
      document.write "<link href=\"" + CommentatorConfig.staticUrl + "commentator/js/lib/prettify/prettify.css\" rel=\"stylesheet\">"
    unless jQuery().markItUp
      document.write "<script src=\"" + CommentatorConfig.staticUrl + "commentator/editor/jquery.markitup.js\"></script>"
      document.write "<link href=\"" + CommentatorConfig.staticUrl + "commentator/editor/editor.css\" rel=\"stylesheet\">"
    document.write "<script src=\"" + CommentatorConfig.staticUrl + "commentator/js/lib/jquery.form.min.js\"></script>"  unless jQuery().ajaxForm
    document.write "<script src=\"" + CommentatorConfig.staticUrl + "commentator/js/lib/jquery.jgrowl.min.js\"></script>"  unless jQuery().jGrowl
    document.write "<script src=\"" + CommentatorConfig.staticUrl + "commentator/js/lib/jquery.sisyphus.min.js\"></script>"  unless jQuery().sisyphus

    # Forms listeners
    $(document).on "click", "#comment-preview-placeholder a", ->
      return

    $(document).on "submit", "#comment-form", (e) ->
      Commentator.comment.save this, $(this).find("[type=\"submit\"]")[0]
      e.preventDefault()
      return


    # Preview and submit
    $(document).on "click touchend", "#comment-form .preview, #comment-form .submit", (e) ->
      if $(this).hasClass("preview")
        Commentator.comment.preview @form, this
      else
        Commentator.comment.save @form, this
      e.preventDefault()
      return

    $(document).on "keydown", "#comment-form", (e) ->
      if e.keyCode is 13
        if e.shiftKey and (e.ctrlKey or e.metaKey)
          $(this).submit()
        else $(this).find("input[type=\"button\"].preview").click()  if e.ctrlKey or e.metaKey
      return


    # Show and hide forms
    $(document).on "click touchend", "#comment-new-link a", (e) ->
      Commentator.forms.comment()
      e.preventDefault()
      return

    $(document).on "click touchend", ".comment-reply a", (e) ->
      id = $(this).parents(".commentator-comment").data("id")
      if $(this).hasClass("reply")
        Commentator.forms.reply id
      else Commentator.forms.edit id  if $(this).hasClass("edit")
      e.preventDefault()
      return

    $(document).ready ->
      if CommentatorConfig.enable_editor
        $("#comment-editor").markItUp(CommentatorConfig.editor)
      $.jGrowl.defaults.closerTemplate = "<div>[ " + CommentatorConfig.close_all_message + " ]</div>"
      count = $(".commentator-comment").size()
      $("#comment-total, .commentator-comments-count").text count

      $("#comment-new-link").hide()  if $("#comment-form").is(":visible")
      return


    # Link to parent comment
    $("#comments").on "click touchend", ".commentator-comment-up a", ->
      id = $(this).data("id")
      parent = $(this).data("parent")
      if parent and id
        Commentator.utils.goto "comment-" + parent
        $("#comment-" + parent + " .commentator-comment-down:lt(1)").show().find("a").attr "data-child", id
      return


    # Link to child comment
    $("#comments").on "click touchend", ".commentator-comment-down a", ->
      child = $(this).data("child")
      Commentator.utils.goto "comment-" + child  if child
      $(this).attr("data-child", "").parent().hide()
      return

    return

  o.comment =
    preview: (form, button) ->
      thread = $("[name=\"thread\"]", form)
      return false  unless thread
      $(form).ajaxSubmit
        data:
          action: "preview"
          thread: thread.val()

        url: CommentatorConfig.actionUrl
        form: form
        button: button
        dataType: "json"
        beforeSubmit: ->
          $(button).attr "disabled", "disabled"
          return

        success: (response) ->
          $(button).removeAttr "disabled"
          if response.success
            $("#comment-preview-placeholder").html(response.data.preview).show()
            prettyPrint()
          else
            Commentator.Message.error response.message
          return
        error: (response)->
          Commentator.Message.error 'Something went wrong!'
          return

      return

    save: (form, button) ->
      thread = $("[name=\"thread\"]", form)
      return false  unless thread
      $(form).ajaxSubmit
        data:
          action: "save"
          thread: thread.val()

        url: CommentatorConfig.actionUrl
        form: form
        button: button
        dataType: "json"
        beforeSubmit: ->
          $(".error", form).text ""
          $(button).attr "disabled", "disabled"
          return

        success: (response) ->
          $(button).removeAttr "disabled"
          if response.success
            Commentator.forms.comment false
            $("#comment-preview-placeholder").html("").hide()
            $("#comment-editor", form).val ""
            $(".commentator-comment .comment-reply a").show()

            if not response.data.comment and response.message
              Commentator.Message.info response.message
            else
              Commentator.comment.insert response.data.comment

            Commentator.utils.goto($(response.data.comment).attr('id'))
            Commentator.comment.getlist()
            prettyPrint()
          else
            Commentator.Message.error response.message
            if response.data
              i = undefined
              field = undefined
              for i of response.data
                field = response.data[i]
                $(form).find("[name=\"" + field.field + "\"]").parent().find(".error").text field.message

          return

        error: (response)->
          Commentator.Message.error 'Something went wrong!'
          return

      return

    getlist: ->
      form = $("#comment-form")
      thread = $("[name=\"thread\"]", form)
      return false  unless thread
      Commentator.tpanel.start()
      $.post CommentatorConfig.actionUrl,
        action: "getlist"
        thread: thread.val()
      ,
        (response) ->
          for k of response.data.comments
            Commentator.comment.insert response.data.comments[k], true  if response.data.comments.hasOwnProperty(k)
          count = $(".commentator-comment").size()
          $("#comment-total, .commentator-comments-count").text count
          Commentator.tpanel.stop()
          return
      ,
        "json"

      return

    insert: (data, remove) ->
      comment = $(data)
      parent = $(comment).attr("data-parent")
      id = $(comment).attr("id")
      exists = $("#" + id)
      children = ""
      if exists.length > 0
        data = comment[0].outerHTML
        if remove
          children += exists.find(".comments-list").html()
          exists.remove()
        else
          exists.replaceWith data
      if parseInt(parent) == 0
        $("#comments").append data
      else
        pcomm = $("#comment-" + parent)
        if CommentatorConfig.thread_depth
          level = pcomm.find(".commentator-comment").size()
          if level > 0
            parent = pcomm.data("parent")
            data = comment.outerHTML
        $("#comment-" + parent + " > .comments-list").append data
      $("#" + id).find(".comments-list").html children  if children.length > 0
      return

  o.forms =
    reply: (comment_id) ->
      $("#comment-new-link").show()
      form = $("#comment-form")
      $(".time", form).text ""
      $(".commentator-comment .comment-reply a").show()
      $("#comment-preview-placeholder").hide()
      $("input[name=\"part_of\"]", form).val comment_id
      $("input[name=\"id\"]", form).val 0
      reply = $("#comment-" + comment_id + " > .comment-reply")
      form.insertAfter(reply).show()
      $("a", reply).hide()
      reply.parents(".commentator-comment").removeClass "commentator-comment-new"
      $("#comment-editor", form).val("").focus()
      return

    comment: (focus) ->
      $("#comment-new-link").hide()
      form = $("#comment-form")
      $(".time", form).text ""
      $(".commentator-comment .comment-reply a:hidden").show()
      $("#comment-preview-placeholder").hide()
      $("input[name=\"part_of\"]", form).val ''
      $("input[name=\"id\"]", form).val 0
      $(form).insertAfter("#comment-form-placeholder").show()
      $("#comment-editor", form).val ""
      $("#comment-editor", form).focus()  if focus
      return

  o.utils =

    goto: (id) ->
      $("html, body").animate
        scrollTop: $("#comment-" + id).offset()
      , 1000
      return

    getCookie: (name) ->
      cookieValue = null
      if document.cookie and document.cookie isnt ""
        cookies = document.cookie.split(";")
        i = 0

        while i < cookies.length
          cookie = jQuery.trim(cookies[i])

          # Does this cookie string begin with the name we want?
          if cookie.substring(0, name.length + 1) is (name + "=")
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          i++
      cookieValue

  o.Message =
    success: (message) ->
      if message
        $.jGrowl message,
          theme: "commentator-message-success"
      return

    error: (message) ->
      if message
        $.jGrowl message, #, sticky: true
          theme: "commentator-message-error"
      return

    info: (message) ->
      if message
        $.jGrowl message,
          theme: "commentator-message-info"

      return

    close: ->
      $.jGrowl "close"
      return
  o.tpanel =
    wrapper: $("#comments-tpanel")
    refresh: $("#tpanel-refresh")
    new_comments: $("#tpanel-new")
    class_new: "commentator-comment-new"
    initialize: ->
      if CommentatorConfig.tpanel
        @wrapper.show()
        @stop()
      @refresh.on "click", ->
        $("." + Commentator.tpanel.class_new).removeClass Commentator.tpanel.class_new
        Commentator.comment.getlist()
        return

      @new_comments.on "click", ->
        elem = $("." + Commentator.tpanel.class_new + ":first")
        $("html, body").animate
          scrollTop: elem.offset().top
        , 1000, "linear", ->
          elem.removeClass Commentator.tpanel.class_new
          return

        count = parseInt(Commentator.tpanel.new_comments.text())
        if count > 1
          Commentator.tpanel.new_comments.text count - 1
        else
          Commentator.tpanel.new_comments.text("").hide()
        return

      return

    start: ->
      @refresh.addClass "loading"
      return

    stop: ->
      count = $("." + @class_new).size()
      if count > 0
        @new_comments.text(count).show()
      else
        @new_comments.hide()
      @refresh.removeClass "loading"
      return

  o)(Commentator or {}, jQuery)

Commentator.init()
Commentator.tpanel.initialize()