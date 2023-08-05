SirTrevor.Blocks.ByLineBlock = (function() {

	var template = _.template([
		'<h2>By line block</h2>',
		'<div class="row">',
		'	<div class="col4"><strong>Text:</strong></div>',
		'	<div class="col8"><input data-text type="text"/></div>',
		'</div>'
	].join('\n'));

	return SirTrevor.Block.extend({

		type: 'by_line_block',

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
			this.$('[data-text]').val(data.quote);
		},

		toData: function() {
			this.setData({
				text: this.$('[data-text]').val()
			});
		}
	});
})();