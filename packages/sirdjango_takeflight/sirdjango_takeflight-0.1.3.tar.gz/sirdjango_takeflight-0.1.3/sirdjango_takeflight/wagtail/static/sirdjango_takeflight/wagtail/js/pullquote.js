SirTrevor.Blocks.PullquoteBlock = (function() {

	var template = _.template([
		'<h2>Pullquote Block</h2>',
		'<div class="row">',
		'	<div class="col4"><strong>Pullquote:</strong></div>',
		'	<div class="col8"><input data-quote type="text"/></div>',
		'</div>',
		'<div class="row">',
		'	<div class="col4"><strong>Source:</strong></div>',
		'	<div class="col8"><input data-source type="text"/></div>',
		'</div>'
	].join('\n'));

	return SirTrevor.Block.extend({

		type: 'pullquote_block',

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
			this.$('[data-quote]').val(data.quote);
			this.$('[data-source]').val(data.source);
		},

		toData: function() {
			this.setData({
				quote: this.$('[data-quote]').val(),
				source: this.$('[data-source]').val()
			});
		}
	});
})();