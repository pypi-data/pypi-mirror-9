/**
  * Javascript code for managing menu forms
  */

(function($){
	$(document).ready(function () {
		
		function manageAddNewElement(data, textStatus) {
			if (data && data.response) {
				// TODO
			}
		}
		
		function newElementMenu(event) {
			var form = $("#customize-factoriesmenu");
			var data = {'element-name': $('#element-name').val(),
			            'element-descr': $('#element-descr').val(),
			            'condition-tales': $('#condition-tales').val(),
			            'element-tales': $('#element-tales').val()};
			data['action'] = 'add';
			$.post("@@customize-factoriesmenu", data, manageAddNewElement, type='json');
			event.preventDefault();
		}
		
		$("#add-new-element-menu").click(newElementMenu);
	});	
})(jQuery);
