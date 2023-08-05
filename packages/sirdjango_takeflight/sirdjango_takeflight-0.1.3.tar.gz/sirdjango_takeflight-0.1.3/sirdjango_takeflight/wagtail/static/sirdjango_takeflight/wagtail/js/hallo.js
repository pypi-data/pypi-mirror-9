/**
 * Hallo.js editor block
 */

SirTrevor.Blocks.Text = (function() {

	// The type string used to identify this block
	var type = 'text';

	var template = _.template([
		'<h2>WYSIWYG Block</h2>',
		'<textarea>&lt;p&gt;&amp;nbsp;&lt;/p&gt;</textarea>',
	].join('\n'));

	// Generate a unique ID for an image
	var newId = (function() {
		var count = 0;
		return function() {
			return ['st', type, ++count].join('-');
		};
	})();

	SirTrevor.EventBus.on('block:create:new block:create:existing', function(block) {
		if (block.blockStorage.type !== type) return;

		var textarea = block.$inner.children('textarea');
		var id = newId();
		textarea.attr('id', id);
		makeRichTextEditable(id);
	}, null);

	return SirTrevor.Block.extend({

		type: type,

		icon_name: 'text',

		timeout: null,

		editorHTML: function() {
			return template(this);
		},

		onBlockRender: function() {
			var textarea = this.$('textarea').hallo();
			textarea.bind('hallomodified', this.onChange);
		},

		onChange: function() {
			// Debounce the onchange event.
			if (this.timeout !== null) {
				clearTimeout(this.timeout);
				this.timeout = null;
			}
			this.timeout = setTimeout(this.toData, 100);
		},

		loadData: function(data){
			var textarea = this.$inner.children('textarea');
			var richtext = this.$inner.children('.richtext');
			textarea.val(data.html);
			richtext.html(data.html);
		},

		toData: function() {
			var textarea = this.$('textarea');
			this.setData({html: textarea.val()});
		}

	});

})();

