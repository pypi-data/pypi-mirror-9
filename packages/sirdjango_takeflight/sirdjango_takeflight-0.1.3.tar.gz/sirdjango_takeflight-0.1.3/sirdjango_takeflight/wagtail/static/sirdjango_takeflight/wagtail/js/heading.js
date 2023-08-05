SirTrevor.Blocks.HeadingBlock = (function() {

	var template = _.template([
		'<h2>Heading 1 Block</h2>',
		'<div class="row">',
		'	<div class="col4"><strong>Heading text:</strong></div>',
		'	<div class="col8"><input class="sirtrevor-heading--text" type="text"/></div>',
		'</div>',
		'<div class="row">',
		'	<div class="col4"><strong>Text color:</strong></div>',
		'	<div class="col8"><input class="sirtrevor-heading--color" type="text"/></div>',
		'</div>'
	].join('\n'));

	return SirTrevor.Block.extend({

		type: 'heading_block',

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
			this.$('.sirtrevor-heading--text').val(data.heading);
			this.$('.sirtrevor-heading--color').val(data.color);
		},

		toData: function() {
			this.setData({
				heading: this.$('.sirtrevor-heading--text').val(),
				color: this.$('.sirtrevor-heading--color').val()
			});
		}
	});
})();