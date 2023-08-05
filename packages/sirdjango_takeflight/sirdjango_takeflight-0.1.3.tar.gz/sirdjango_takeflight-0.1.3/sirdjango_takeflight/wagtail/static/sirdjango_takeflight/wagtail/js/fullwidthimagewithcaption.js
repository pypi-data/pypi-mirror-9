/**
 * Wagtail image chooser widget
 */

SirTrevor.Blocks.FullwidthImageWithCaptionBlock = (function() {

	// The type string used to identify this block
	var type = 'fullwidth_image_with_caption_block';

	var template = _.template([
		'<h2>Fullwidth Image Block With Caption</h2>',
		'<div class="chooser image-chooser blank">',
		'	<div class="chosen">',
		'		<div class="preview-image">',
		'			<img data-image-thumb />',
		'		</div>',
		'		<div class="actions">',
		'			<input type="button" class="action-clear button-small button-secondary" value="Clear choice">',
		'			<input type="button" class="action-choose button-small button-secondary" value="Choose another item">',
		'		</div>',
		'	</div>',
		'	<div class="unchosen">',
		'		<input type="button" class="action-choose button-small button-secondary" value="Choose an image">',
		'	</div>',
		'</div>',
		'<input data-image-id type="hidden" />',
		'<div class="field">',
		'	<label>Caption:</label>',
		'	<div class="field-content">',
		'		<div class="input">',
		'			<input data-image-caption />',
		'		</div>',
		'	</div>',
		'</div>'
	].join('\n'));

	// Generate a unique ID for an image
	var newId = (function() {
		var count = 0;
		return function() {
			return ['st', type, ++count].join('-');
		};
	})();

	// Initialize the image chooser widget when the block is created
	SirTrevor.EventBus.on('block:create:new block:create:existing', function(block) {
		if (block.blockStorage.type !== type) return;

		block.$inner.find('input').each(function() {
			var id = newId();
			console.log('here', id);
			$(this).attr('id', id);
			$(this).prev('.image-chooser').attr('id', id + '-chooser');
			createImageChooser(id);
		});
	}, null);

	return SirTrevor.Block.extend({

		type: type,

		icon_name: 'image',

		editorHTML: function() {
			return template(this);
		},

		onChange: function() {
			this.toData();
		},

		loadData: function(data){
			this.$('input[data-image-id]').val(data.image_id);
			this.$('input[data-image-caption]').val(data.caption);
			this.$('.image-chooser').removeClass('blank');
			this.$('img[data-image-thumb]').replaceWith(data.image_tag);
		},

		toData: function() {
			this.setData({
				image_id: this.$('[data-image-id]').val(),
				caption: this.$('[data-image-caption]').val()
			});
		}

	});

})();
