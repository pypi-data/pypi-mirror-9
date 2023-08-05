/**
 * Djinn forms JS lib. Mainly helper functions for form widget handling.
 * TODO: put relate widget JS into separate file, and add to widget media
 */

if (djinn === undefined) {
    var djinn = {};
}


if (djinn.forms === undefined) {
  djinn.forms = {};
}


/**
 * Given an input, remove the value from the list of values. Assumes
 * that the input contains multiple values separated by <separator>.
 * @param input Input element (jQuery object)
 * @param value Value to remove
 * @param separator Value separator, defaults to ';;'
 */
djinn.forms.removeValue = function(input, value, separator) {

  var new_values = [];
  var old_values = input.val() || "";
  var sep = (separator || ";;");

  old_values = old_values.split(sep);

  for (var i = 0; i < old_values.length; i++) {

    if (old_values[i] != value) {
      new_values.push(old_values[i]);
    }
  }

  input.val(new_values.join(sep));
};


/**
 * Add value to ';;' separated values list.
 * @param input Input element (jQuery object)
 * @param value Value to add
 * @param unique If set, double values are removed
 * @param separator Value separator, defaults to ';;'
 */
djinn.forms.addValue = function(input, value, unique, separator) {

  var sep = (separator || ";;");

  if (!input.val()) {
    input.val(value);
  } else {
    if (!unique) {
      input.val(input.val() + sep + value);
    } else {
      var new_values = [];
      var old_values = input.val();

      old_values = old_values.split(sep);

      for (var i = 0; i < old_values.length; i++) {

        if (old_values[i] != value) {
          new_values.push(old_values[i]);
        }
      }
      new_values.push(value);

      input.val(new_values.join(sep));
    }
  }
};


djinn.forms.hasValue = function(input, value, separator) {

  var sep = (separator || ";;");

  if (!input.val()) {
    return false;
  } else {

    var old_values = input.val();

    old_values = old_values.split(sep);

    for (var i = 0; i < old_values.length; i++) {
      
      if (old_values[i] == value) {
        return true;
      }
    }

    return false;
  }
};


/**
 * Initialize file uploader widget.
 */
djinn.forms.init_fileuploader = function(options) {

  var defaults = {
    url: '/fileupload',
    dataType: 'json',
    progressInterval: 10,
    done: function (e, data) {

      var valuetgt = $($(e.target).data("valuefield"));
      var tgt = $(e.target);

      if (tgt.attr("multiple") && tgt.attr("multiple") != "false") {
        $(tgt.data("target")).append(data.result.html);
        valuetgt.val(valuetgt.val() + "," + data.result.attachment_ids.join(","));
      } else {
        $(tgt.data("target")).html(data.result.html);
        valuetgt.val(data.result.attachment_ids[0]);
      }

      $(tgt.data("progress") + " .bar").css("width", "100%");

      if (tgt.data("callback")) {

        var callback = eval(tgt.data("callback"));
        callback.apply(null, tgt);
      }

      tgt.parents(".imagewidget").removeClass("loading");

      $(document).triggerHandler("djinn_forms_fileupload_done", [e.target, data.result]);
    },
    send: function(e, data) {
      $(document).triggerHandler("djinn_forms_fileupload_send", [e.target]);

      var tgt = $(e.target);

      tgt.parents(".imagewidget").addClass("loading");

      $($(e.target).data("progress") + " .bar").css("width", "5%");
    },
    progressall: function (e, data) {

      var progress = parseInt(data.loaded / data.total * 100, 10);

      $($(e.target).data("progress") + " .bar").css("width", progress + "%");
    }
  };

  if (options) {
    $.extend(defaults, options);
  }

  $("input[type='file']").each(function() {

      if ($(this).data("uploadurl")) {
        defaults.url = $(this).data("uploadurl");
      }
      defaults.dropZone = $(this).attr("id");

      defaults.formData = {
        "attachment_id": $(this).hasClass("field") ? $($(this).data("valuefield")).val() : "",
        "attachment_type": $(this).data("attachmenttype"),
        "edit_type": $(this).hasClass("field") ? "field": "attachment"
      };

      $(this).fileupload(defaults);
    });
};


djinn.forms.remove_attachment = function(elt, attachment_id) {

  var input = $(elt.parents(".fileupload").find("input[type='file']").eq(0).data("valuefield"));

  djinn.removeValue(input, attachment_id, ",");

  $(document).triggerHandler("djinn_forms_fileupload_remove", elt);
};


$(document).ready(function() {

    $('.date').datepicker();
    $('.time').datetimepicker({timeOnly: true});

    $(document).on("click", ".attach .delete ", function(e) {

        e.preventDefault();

        var widget = $(e.currentTarget).parents(".attach");
        var record = $(e.currentTarget).parents("li");
        var link = $(e.currentTarget);

        djinn.forms.removeValue(widget.find(".value-list").eq(0),
                                link.data("value"));

        record.remove();

        $(document).trigger("djinn_forms_detach", [widget, link.data("value")]);
      });

    $(document).on("click", ".imagewidget .delete-image", function(e) {
        var tgt = $(e.currentTarget);

        $(tgt.data("target")).val("");
        tgt.parents(".imagewidget").addClass("empty");
        tgt.parents(".imagewidget").find(".uploads").html("");

        e.preventDefault();
      });

    $(document).on("djinn_forms_fileupload_done", function(e, target, result) {

        if ($(target).parents(".imagewidget")) {
          $(target).parents(".imagewidget").removeClass("empty");
        }
      });
  });
