/**
 * Unicorn Admin Template
 * Diablo9983 -> diablo9983@gmail.com
**/
$(document).ready(function(){

	// === Sendit custom classes === //
	$.ZTFY.sendit = {

		form: {

			/**
			 * Add a new document to documents upload form
			 */
			addDocument: function(source) {
				var button = $(source).parents('DIV.widgets-suffix');
				var document = button.prev();
				// Get widgets values
				var file_input = $('INPUT[name="documents.widgets.data"], INPUT[name="documents.widgets.data:list"]', document);
				if (!file_input.val())
					return;
				// Clone initial document
				var new_document = document.clone();
				var list = $('DIV.documents_list').removeClass('hidden');
				$('DIV.label', document).hide();
				// Get components and values
				var title = $('INPUT[name="documents.widgets.title"], INPUT[name="documents.widgets.title:list"]', document);
				var hidden_title = $('<input type="hidden" name="documents.widgets.title" />').val(title.val());
				// Create new components
				$('<span>').text(hidden_title.val()).insertAfter(title);
				title.replaceWith(hidden_title);
				file_input.attr('disabled', true);
				$('<i>').attr('class', 'icon icon-trash')
						.attr('title', "Enlever ce document")
						.click($.ZTFY.sendit.form.removeDocument)
						.insertAfter(file_input);
				document.detach()
						.appendTo(list);
				$('INPUT, INPUT', new_document).val(null);
				new_document.insertBefore(button);
				// Check for hiding button when adding "max documents count" documents
				var actions = $(source).parents('DIV.actions');
				var max_documents = actions.data('sendit-documents-count');
				var nb_documents = $('DIV.widgets', list).length;
				if ((nb_documents != 0) && (nb_documents >= max_documents-1))
					$(source).attr('disabled', true);
			},

			/**
			 * Remove an upload entry from upload form
			 */
			removeDocument: function(event) {
				$(this).parents('DIV.widgets').remove();
				$('INPUT:button', $('DIV.widgets-suffix DIV.actions')).attr('disabled', false);
			},

			/**
			 * Remove an existing document
			 */
			removeOldDocument: function(source) {
				$(source).parents('DIV.item').remove();
			},

			/**
			 * Check documents upload
			 */
			checkDocumentsUpload: function(form, input) {
				var id = $(input).data('sendit-documents-group');
				var subform = $('DIV[id="'+id+'"]', form);
				$('INPUT:text, INPUT:hidden, INPUT:radio, INPUT:file, TEXTAREA', subform).each(function(index, element) {
					var name = $(element).attr('name');
					if (name && !name.endsWith(':list')) {
						$(element).attr('name', name + ':list');
					}
				});
				$('INPUT:file', subform).attr('disabled', false);
			},

			/**
			 * Check documents upload entries
			 */
			checkDocumentsInputs: function(form, input) {
				var id = $(input).data('sendit-documents-id');
				var name = $(input).data('sendit-documents-name');
				var upload_ok = !$('INPUT[id="'+id+'"]').hasClass('required');
				var last_index = -1;
				$('INPUT[id^="'+id+'"]', $('DIV.document')).each(function(index, element) {
					$(element).attr('id', id + '-' + index)
							  .attr('name', name + '.' + index);
					if ($(element).val()) {
						upload_ok = true;
					}
					last_index = index;
				});
				$('INPUT[name="'+name+'.count"]', form).val(last_index+1);
				if (upload_ok) {
					return true;
				} else {
					return ' - vous devez fournir au moins un document à télécharger !!';
				}
			},

			/**
			 * Remove user packet
			 */
			deletePacketCallback: function(result, status) {
				if (status == 'success') {
					if (typeof(result) == "string")
						result = $.parseJSON(result);
					var output = result.output;
					switch (output) {
						case 'OK':
							var button = $('DIV[id="delete_' + result.packet_oid + '"]');
							button.closest('TR').remove();
					}
					$.ZTFY.dialog.close();
				}
			}
		},

		/**
		 * Profile management
		 */
		profile: {

			openDialog: function(source) {
				var uid = $('INPUT[name="principal_id"]', 'FIELDSET.profile-search').val();
				if (uid)
					$.ZTFY.dialog.open('@@profile_edit.html?uid=' + uid);
			}
		}
	}

	$('FIELDSET.profile-search').on('click', 'A.bit-box', $.ZTFY.sendit.profile.openDialog);

});
