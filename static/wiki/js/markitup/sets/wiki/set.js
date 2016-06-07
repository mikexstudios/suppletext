// -------------------------------------------------------------------
// markItUp!
// -------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// -------------------------------------------------------------------
// Mediawiki Wiki tags example
// -------------------------------------------------------------------
// Feel free to add more tags
// -------------------------------------------------------------------
mySettings = {
	previewParserPath:	'', // path to your Wiki parser
	onShiftEnter:		{keepDefault:false, replaceWith:'\\\\\n'},
	markupSet: [
		{name:'Heading 1', openWith:'= ', closeWith:' =', placeHolder:'Your title here...' },
		{name:'Heading 2', openWith:'== ', closeWith:' ==', placeHolder:'Your title here...' },
		{name:'Heading 3', openWith:'=== ', closeWith:' ===', placeHolder:'Your title here...' },
		{name:'Heading 4', openWith:'==== ', closeWith:' ====', placeHolder:'Your title here...' },
		{name:'Heading 5', openWith:'===== ', closeWith:' =====', placeHolder:'Your title here...' },
		{separator:'---------------' },		
		{name:'Bold', openWith:"**", closeWith:"**"}, 
		{name:'Italic', openWith:"//", closeWith:"//"}, 
		//{name:'Strike-through', key:'S', openWith:'<s>', closeWith:'</s>'}, 
		{separator:'---------------' },
		//{name:'Bulleted list', openWith:'(!(* |!|*)!)'}, 
		{name:'Bulleted list', openWith:'* '}, 
		//{name:'Numeric list', openWith:'(!(# |!|#)!)'}, 
		{name:'Numeric list', openWith:'# '}, 
		{separator:'---------------' },
		{name:'Picture', replaceWith:'{{[![Url of image:!:http://]!]|[![Alternate text:!:My Image]!]}}'}, 
		{name:'Link', openWith:"[[![Link]!] ", closeWith:']', placeHolder:'Your text to link here...' },
		{name:'Url', openWith:"[[![Url:!:http://]!] ", closeWith:']', placeHolder:'Your text to link here...' },
		//{separator:'---------------' },
		//{name:'Quotes', openWith:'(!(> |!|>)!)', placeHolder:''},
		//{name:'Code', openWith:'(!(<source lang="[![Language:!:php]!]">|!|<pre>)!)', closeWith:'(!(</source>|!|</pre>)!)'}, 
		//{separator:'---------------' },
		//{name:'Preview', call:'preview', className:'preview'}
	]
}
