// Fill fields in bulk edit and split asset forms

var FieldsFiller = function () {};
FieldsFiller.prototype.copyAutocompletedValue = function(src, dst) {
  /*
  Copy autocompleted field value (like: model, category, user, etc.) from
   *src* to *dst*.
  Both *src* and *dst* are regular inputs in autocompleter.
  */
  var errorMsg = "Can't find hidden input within: ";
  var hidSrc = $($(src).parent()).find('input:hidden');
  var hidDst = $($(dst).parent()).find('input:hidden');
  if (hidSrc.length === 0) {
      throw new Error(errorMsg + $(src).parent().html());
  }
  if (hidDst.length === 0) {
      throw new Error(errorMsg + $(el).parent().html());
  }
  hidDst.val(hidSrc.val()).trigger(
      {type: 'change', cloneSource: hidSrc}
  );
};

$(document).ready(function () {
  var fieldsFiller = new FieldsFiller();
  // Disable autocomplete without cluttering html attributes
  $('input').attr('autocomplete', 'off');

  /* After closing datepicker toogle toolbar */
  $('.datepicker').on('changeDate', function (ev) {
      toggle_toolbar(this);
  });

  $("input[type=text].fillable,select.fillable").blur(function (event) {
      $("#float_toolbar").hide();
  });

  var toggle_toolbar = function (input) {
      var toolbar = $("#float_toolbar");
      var offset = $(input).offset();
      var width = input.clientWidth;
      var height = input.clientHeight;
      var distance_left = 0;
      var distance_top = 0;

      /* Clear data */
      $(toolbar).data('input_name', '');
      $(toolbar).data('input_id', '');

      /* For fields without id set, save its name as selector */
      if (input.id === '') {
          $(toolbar).data('input_name', input.name);
      } else {
          $(toolbar).data('input_id', input.id);
      }
      toolbar.css("left", parseInt(offset.left) + width + distance_left + "px");
      toolbar.css("top", parseInt(offset.top) + height + distance_top + "px");
      toolbar.show();
  };

  $("input[type=text].fillable,select.fillable").focus(function (event) {
      toggle_toolbar(this);
  });

  $("#fill_all_rows").mousedown(function (event) {
      var MAX_ROWS = 100;
      var input_id = $("#float_toolbar").data('input_id');
      var input_name = $("#float_toolbar").data('input_name');
      var matcher = /(.*)-([0-9]+)-(.*)/;
      var results, pre, number, post, value_to_fill, el, sourceField;
      if (input_id != '') {
          results = matcher.exec(input_id);
          sourceField = $('#' + input_id);
      } else if (input_name != '') {
          results = matcher.exec(input_name);
          sourceField = $('input[name="' + input_name + '"]');
      }
      pre = results[1];
      number = results[2];
      post = results[3];
      for (var i = 0; i < MAX_ROWS; i++) {
          if (input_id != '') {
              el = $('#' + pre + "-" + i + "-" + post);
          } else {
              el = $('input[name="' + pre + "-" + i + "-" + post + '"]');
          }
          var dstIsSrc = $(sourceField).attr('id') === $(el).attr('id');
          if (dstIsSrc) {
              continue;
          }
          if (!el.length) {
              break;
          }
          var isAutocompleter = $(el).hasClass('ui-autocomplete-input');
          if (isAutocompleter) {
            fieldsFiller.copyAutocompletedValue(sourceField, el);
          } else {
            el.val(sourceField.val());
          }
      }
      $("#float_toolbar").hide();
      return false;
  });
});
