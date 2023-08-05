SirTrevor.Blocks.AdditionalInfoBlock = (function() {

	var template = _.template([
		'<h2>Additional Info Block</h2>',
		'<div class="row">',
		'	<div class="col4"><strong>Title:</strong></div>',
		'	<div class="col8"><input data-title type="text"/></div>',
		'</div>',
		'<div class="row">',
		'	<div class="col4"><strong>Text:</strong></div>',
		'	<div class="col8"><input data-text type="text"/></div>',
		'</div>'
	].join('\n'));

	return SirTrevor.Block.extend({

		type: 'additional_info_block',

		icon_name: 'text',

		editorHTML: function() {
			return template(this);
		},

		onChange: (function() {
			var timeout = null;
			return function(e) {
				if (timeout) {
					clearTimeout(timeout);
					timeout = null;
				}
				timeout = setTimeout(this.toData, 100);
			};
		})(),

		loadData: function(data){
			this.$('[data-title]').val(data.title);
			this.$('[data-text]').val(data.text);
		},

		toData: function() {
			this.setData({
				title: this.$('[data-title]').val(),
				text: this.$('[data-text]').val()
			});
		}
	});
})();