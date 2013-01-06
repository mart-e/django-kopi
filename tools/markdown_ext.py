import markdown

class RestrictiveMarkdownExtension(markdown.Extension):

	def extendMarkdown(self, md, md_globals):
		del md.inlinePatterns['image_link']
		del md.inlinePatterns['image_reference']
