/*global jQuery */

(function(window, $) {
  'use strict';

  function updateMediumFromTextareas(event) {
    var ta = $(event.target);
    if (((event.type == 'keyup' || event.type == 'paste') && ta.is(':focus')) || event.type == 'blur') {
      var elem_jq = $('#' + ta.attr('id') + '-wysiwyg');
      elem_jq.html(ta.val());
    }
  }

  $(function() {
    var elements = document.querySelectorAll('.medium-editable');

    $.each(elements, function(i, elem) {
      var elem_jq = $(elem);
      var elem_id = elem_jq.attr('id');
      var ta_id = elem_id.replace('-wysiwyg', '');
      var ta = $('#' + ta_id);

      if (ta.val()) {
        elem_jq.html(ta.val());
      }

      var medium_editor_options = {
        buttons: [
          'bold',
          'italic',
          'underline',
          'anchor',
          'unorderedlist',
          'orderedlist',
          'indent',
          'outdent',
          'header1',
          'header2',
          'quote',
          'justifyLeft',
          'justifyRight',
          'justifyCenter'],
        buttonLabels: 'fontawesome',
        cleanPastedHTML: true,
        staticToolbar: true,
        stickyToolbar: true,
        targetBlank: true
      };

      if (typeof MEDIUM_FIRST_HEADER !== 'undefined') {
        medium_editor_options['firstHeader'] = MEDIUM_FIRST_HEADER;
      }
      if (typeof MEDIUM_SECOND_HEADER !== 'undefined') {
        medium_editor_options['secondHeader'] = MEDIUM_SECOND_HEADER;
      }

      var editor = new MediumEditor(elem, medium_editor_options);

      if (typeof MEDIUM_IMAGE_UPLOAD_URLS !== 'undefined' && ta_id in MEDIUM_IMAGE_UPLOAD_URLS) {
        elem.focus();
        elem_jq.mediumInsert({
          editor: editor,
          addons: {
            images: {
              uploadScript: MEDIUM_IMAGE_UPLOAD_URLS[ta_id],
              deleteScript: MEDIUM_IMAGE_DELETE_URLS[ta_id]
            },
            embeds: {
              oembedProxy: 'http://medium.iframe.ly/api/oembed?iframe=1'
            }
          }
        });
      }

      $('body').on('input', elem_jq, function(event) {
        var allContents = editor.serialize();
        var allContentsValue = allContents[elem_id].value;

        // Need to be careful to avoid copying WYSIWYG contents
        // to hidden textarea, if there's a base64 image chucked
        // in the text at this moment.
        if (!(/data\:[^\;]+\;base64/.test(allContentsValue))) {
          ta.val(allContentsValue)
            .trigger('keyup');
        }
      });

      var buttonWaitingText = ' (waiting for images to upload...)';

      var buttonWaiting = function(button) {
        var allContents = editor.serialize();
        var allContentsValue = allContents[elem_id].value;

        if (!(/data\:[^\;]+\;base64/.test(allContentsValue))) {
          button.removeAttr('disabled')
              .html(button.html().replace(buttonWaitingText, ''))
              .trigger('click');
        }
        else {
          setTimeout(function() {
            buttonWaiting(button);
          }, 2000);
        }
      };

      $('body').on('click', 'button#button-submit, button#button-save', function(event) {
        var button = $(this);
        var allContents = editor.serialize();
        var allContentsValue = allContents[elem_id].value;

        // Need to be careful to avoid copying WYSIWYG contents
        // to hidden textarea, if there's a base64 image chucked
        // in the text at this moment.
        if (!(/data\:[^\;]+\;base64/.test(allContentsValue))) {
          ta.val(allContentsValue);
        }

        // If an image has recently been uploaded, seems that we
        // need to serialize and check for base64 data twice
        // (with a little sleep in between), otherwise it doesn't
        // refresh properly.
        if (/data\:[^\;]+\;base64/.test(allContentsValue)) {
          button.html(button.html() + buttonWaitingText);
          $('button#button-submit, button#button-save').attr('disabled', 'disabled');

          setTimeout(function() {
            buttonWaiting(button);
          }, 2000);

          return false;
        }
        else {
          return true;
        }
      });

      ta.hide();
      $('body').on('blur keyup paste', ta, updateMediumFromTextareas);

      if (ta.val()) {
        elem_jq.trigger('click');
      }
    });

    $('.title-image-wrapper .editable-wrapper, .medium-editable')
      .before('<div class="edit-icon-wrapper"><span class="glyphicon glyphicon-pencil"></span></div>')
      .hover(function() {
          var editableEl = $(this);
          if (!$(this).hasClass('medium-editable')) {
            editableEl = editableEl.find('input[type=text]');
          }

          editableEl.addClass('active');
          $(this).prev('.edit-icon-wrapper').find('.glyphicon').wrap('<a />');
        },
        function() {
          var editableEl = $(this);
          if (!$(this).hasClass('medium-editable')) {
            editableEl = editableEl.find('input[type=text]');
          }

          editableEl.removeClass('active');
          if ($(this).prev('.edit-icon-wrapper').find('.glyphicon').parent('a').length) {
            $(this).prev('.edit-icon-wrapper').find('.glyphicon').unwrap();
          }
        });
  });
})(window, jQuery);
