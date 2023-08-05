{% load i18n djaloha_utils %}
(function (window, undefined) {
	var Aloha = window.Aloha || ( window.Aloha = {} );
	Aloha.settings = {
        {% if config.jquery_no_conflict %}
        jQuery: $.noConflict(true),
        {% endif %}
        logLevels: { 'error': true, 'warn': true, 'info': true, 'debug': false, 'deprecated': true },
		errorhandling: false,
		ribbon: false,
		locale: "{%if LANGUAGE_CODE|length > 2%}{{LANGUAGE_CODE|slice:':2'}}{%else%}{{LANGAGE_CODE}}{%endif%}",
		floatingmenu: {
			"behaviour" : "float"
		},
		sidebar: {
			disabled: {{config.sidebar_disabled}}
		},
        repositories: {
            linklist: {
		    	data: [{% for link in links %}
                    { name: "{{link.title|convert_crlf}}", url: '{{link.get_absolute_url}}', type: 'website', weight: 0.50 }{%if not forloop.last %},{%endif%}
                {% endfor %}]
			}
		},
		contentHandler: {
			insertHtml: [ 'word', 'generic', 'oembed', 'sanitize' ],
			initEditable: [ 'sanitize' ],
			getContents: [ 'blockelement', 'sanitize', 'basic' ],
			sanitize: 'relaxed', // relaxed, restricted, basic,
			allows: {
				elements: [
					'strong', 'em', 'i', 'b', 'blockquote', 'br', 'cite', 'code', 'dd', 'div', 'dl', 'dt', 'em',
					'a', 'li', 'ol', 'p', 'pre', 'q', 'small', 'strike', 'sub',
					'sup', 'u', 'ul', 'iframe', 'img', 'table', 'tbody', 'tr', 'td',
					'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr'
				],
				attributes: {
					'a'         : ['href', 'target'],
					'blockquote': ['cite'],
					'q'         : ['cite'],
					'p'			: ['style'],
					'iframe'	: ['height', 'width', 'src', 'frameborder', 'allowfullscreen'],
					'img'		: ['height', 'width', 'src', 'style']
				},
		 
				protocols: {
					'a'         : {'href': ['ftp', 'http', 'https', 'mailto', '__relative__', 'courrier']}, // Sanitize.RELATIVE
					'iframe'    : {'src': ['ftp', 'http', 'https', '__relative__']}, // Sanitize.RELATIVE
					'img'    	: {'src': ['ftp', 'http', 'https', '__relative__']}, // Sanitize.RELATIVE
					'blockquote': {'cite': ['http', 'https', '__relative__']},
					'q'         : {'cite': ['http', 'https', '__relative__']}
				}
			}
		},
		plugins: {
			format: {
				// all elements with no specific configuration get this configuration
				config: [  'b', 'i', 'u', 'del', 'p', 'sub', 'sup', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'removeFormat' ],
				{% if config.css_classes %}
				allowedClasses : [{% for cls in config.css_classes %}
                    '{{ cls }}'{%if not forloop.last %},{%endif%}
                {% endfor %}],
				{% endif %}
                editables: {
					// no formatting allowed for title
					'#top-text': ['title']
				}
			},
			list: {
				// all elements with no specific configuration get an UL, just for fun :)
				config: [ 'ul', 'ol' ],
				editables: {
					// Even if this is configured it is not set because OL and UL are not allowed in H1.
					'#top-text': []
				}
			},
			listenforcer: {
				editables: [ '.aloha-enforce-lists' ]
			},
			abbr: {
				// all elements with no specific configuration get an UL, just for fun :)
				config: [ 'abbr' ],
				editables: {
					// Even if this is configured it is not set because OL and UL are not allowed in H1.
					'#top-text': []
				}
			},
			link: {
				// all elements with no specific configuration may insert links
				config: [ 'a' ],
				editables: {
					// No links in the title.
					'#top-text': []
				},
				// all links that match the targetregex will get set the target
                // e.g. ^(?!.*aloha-editor.com).* matches all href except aloha-editor.com
				targetregex : '^http.*',
				// this target is set when either targetregex matches or not set
				// e.g. _blank opens all links in new window
				target: '_blank',
				// the same for css class as for target
				//cssclassregex: '^(?!.*aloha-editor.com).*',
				//cssclass: 'djaloha-editable',
				// use all resources of type website for autosuggest
				objectTypeFilter: ['page', 'website']
				/* handle change of href
				onHrefChange: function ( obj, href, item ) {
					var jQuery = Aloha.require( 'aloha/jquery' );
					if ( item ) {
						jQuery( obj ).attr( 'data-name', item.name );
					} else {
						jQuery( obj ).removeAttr( 'data-name' );
					}
				}*/
			},
			/*table: {
				// all elements with no specific configuration are not allowed to insert tables
				config: [ 'table' ],
				editables: {
					// Don't allow tables in top-text
					'#top-text': [ '' ]
				},
				summaryinsidebar: true,
					// [{name:'green', text:'Green', tooltip:'Green is cool', iconClass:'GENTICS_table GENTICS_button_green', cssClass:'green'}]
				tableConfig: [
					{ name: 'hor-minimalist-a' },
					{ name: 'box-table-a' },
					{ name: 'hor-zebra' },
				],
				columnConfig: [
					{ name: 'table-style-bigbold',  iconClass: 'aloha-button-col-bigbold' },
					{ name: 'table-style-redwhite', iconClass: 'aloha-button-col-redwhite' }
				],
				rowConfig: [
					{ name: 'table-style-bigbold',  iconClass: 'aloha-button-row-bigbold' },
					{ name: 'table-style-redwhite', iconClass: 'aloha-button-row-redwhite' }
				]
			},*/
			table: {
				// all elements with no specific configuration are not allowed to insert tables
				config : [ 'table' ],
				
				// the table summary is editable in the sidebar
				summaryinsidebar : true,
				// the following settings allow the user to apply specific classes to
				// either the whole table or a column or row. The name is used as a
				// class attribute, while the iconClass is applied as a class attribute
				// to style the buttons
				tableConfig : [
					{ name:'hor-minimalist-a' },
					{ name:'box-table-a' },
					{ name:'hor-zebra' },
				],
				columnConfig : [
						{ name: 'table-style-bigbold',  iconClass: 'aloha-button-col-bigbold' },
						{ name: 'table-style-redwhite', iconClass: 'aloha-button-col-redwhite' }
				],
				rowConfig : [
						{ name: 'table-style-bigbold',  iconClass: 'aloha-button-row-bigbold' },
						{ name: 'table-style-redwhite', iconClass: 'aloha-button-row-redwhite' }
				],
				cellConfig : [
						{ name: 'table-style-bigbold',  iconClass: 'aloha-button-row-bigbold' },
						{ name: 'table-style-redwhite', iconClass: 'aloha-button-row-redwhite' }
				],
				// allow resizing the table width (default: true)
				tableResize: true,
				// allow resizing the column width (default: true)
				colResize: true,
				// allow resizing the row height (default: true)
				rowResize: true
			},
            image: {
				'fixedAspectRatio' : false,
				'maxWidth'         : 600,
				'minWidth'         : 20,
				'maxHeight'        : 600,
				'minHeight'        : 20,
				'globalselector'   : '.global',
				'autoResize': false,
				'ui': {
					'resizable' : {% if resize_disabled %}false{% else %}true{% endif %},
					'crop' : false
				}
			},
			cite: {
				referenceContainer: '#references'
			},
			formatlesspaste: {
				config: {
					button: true, // if set to false the button will be hidden
					formatlessPasteOption: true, // default state of the button
					strippedElements: [ // elements to be stripped from the pasted code
						"span",
                  		"font",
                  		"style",
						"em",
						"strong",
						"small",
						"s",
						"cite",
						"q",
						"dfn",
						"abbr",
						"time",
						"code",
						"var",
						"samp",
						"kbd",
						"sub",
						"sup",
						"i",
						"b",
						"u",
						"mark",
						"ruby",
						"rt",
						"rp",
						"bdi",
						"bdo",
						"ins",
						"del"
					]
				}
			}
		}
	};

})(window);

