# -*- coding: utf-8 -*-

catalog_default_css = '''
	body { background-color: white; margin: 0px; padding: 0px; font-size: 12px; font-family: verdana; }
	div.catName { padding: 10px; background-color: #70803C; font-size: 20px; color: white; }
	div.catDesc { padding: 20px 20px 10px; }
	ul.catService { }
	ul.catService li { padding-bottom: 10px; }
	div.catInterfaces { padding: 0px 10px 10px 30px; }
	div.catGen { text-align: center; font-style: italic; margin-top: 20px; margin-bottom: 20px; } 
'''

service_default_css = '''
	body { margin: 0px; padding: 0px; font-family: verdana; font-size: 12pt; background-color: #FCFCFC; }

	div.service-header {
		height: 34px;
		font-weight: bold; padding: 10px; font-size: 30px; color: white; border-bottom: 1px solid black; background: #70803C;
		filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#A0B06C', endColorstr='#70803C'); background: -webkit-gradient(linear, left top, left bottom, from(#A0B06C), to(#70803C)); background: -moz-linear-gradient(top,  #A0B06C,  #70803C);
		text-shadow: #555555 2px 3px 3px;
	}
	div.service-header div.service-title {position: relative; float:left}
	div.service-header .skin-selector {padding-top: 8px; margin-bottom: 0; position:relative; float: right; font-size: 12pt;}

	div.service-overview {
		float: right; margin: 20px; width: 200px;
		-moz-border-radius: 7px 7px 7px 7px; -webkit-border-radius: 7px 7px 7px 7px; border-radius: 7px 7px 7px 7px; background-color: #F6F6F6; border: 1px solid #E6E6E6; border-collapse: separate; font-size: 11px; padding: 10px; margin-right: 20px;
		-moz-box-shadow: 2px 2px 4px #555; -webkit-box-shadow: 2px 2px 4px #555; box-shadow: 2px 2px 4px #555;
	}

	div.service-overview div.headline { font-weight: bold; font-size: 18px; }
	div.service-overview div.title { font-weight: bold; margin: 4px; font-size: 1.2em; }
	div.service-overview ul.list { padding: 0px; margin: 0px; margin-left: 15px; list-style-type: none; }
	div.service-overview ul.list li { font-size: 1.1em; }

	div.service-description { padding: 15px; padding-bottom: 0px; }
	div.service-description div.title { font-weight: bold; font-size: 1.2em; }
	div.service-description div.doc-lines { font-size: 0.8em; }
	div.service-description p.url { font-size: 0.8em; font-style: italic; }
	div.service-description p.url span.url-title { font-weight: bold; }

	div.service-interfaces { padding: 15px; padding-bottom: 0px;  }
	div.service-interfaces div.title { font-weight: bold; font-size: 1.2em; }
	div.service-interfaces ul.list { font-size: 0.8em; }
	div.service-interfaces ul.list li { padding: 4px; }

	div.service-api { padding: 15px; padding-bottom: 0px;  }
	div.service-api div.methods div.title { font-weight: bold; font-size: 1.2em; } 
	div.service-api div.methods ul.list { font-size: 0.9em; list-style-type: none; } 
	div.service-api div.methods ul.list li.entry {
		-moz-border-radius: 7px 7px 7px 7px; -webkit-border-radius: 7px 7px 7px 7px; border-radius: 7px 7px 7px 7px; background-color: #F6F6F6; border: 1px solid #E6E6E6; 
		border-collapse: separate; font-size: 0.8em; padding: 10px; margin-right: 20px;
		-moz-box-shadow: 2px 2px 5px #555; -webkit-box-shadow: 2px 2px 5px #555; box-shadow: 2px 2px 5px #555;
		margin-bottom: 16px;
	} 
	div.service-api div.methods ul.list li.entry div.declaration {
		font-size: 1.5em;
	} 
	div.service-api div.methods ul.list li.entry div.declaration span.name { color: #881a1a; } 
	div.service-api div.methods ul.list li.entry span.param-type { color: #68387f; } 
	div.service-api div.methods ul.list li.entry span.param-name {} 
	div.service-api div.methods ul.list li.entry div.doc-lines { font-size: 1.2em; color: #276d11; } 
	div.service-api div.methods ul.list li.entry ul.params div.doc-lines { margin-top:0;margin-bottom:6px; font-size: 1.0em; color: #276d11; } 

	div.service-api div.types div.title { font-weight: bold; font-size: 1.2em; } 
	div.service-api div.types ul.list { font-size: 0.9em; list-style-type: none; } 
	div.service-api div.types ul.list li.entry {
		-moz-border-radius: 7px 7px 7px 7px; -webkit-border-radius: 7px 7px 7px 7px; border-radius: 7px 7px 7px 7px; background-color: #F6F6F6; border: 1px solid #E6E6E6; 
		border-collapse: separate; font-size: 0.8em; padding: 10px; margin-right: 20px;
		-moz-box-shadow: 2px 2px 5px #555; -webkit-box-shadow: 2px 2px 5px #555; box-shadow: 2px 2px 5px #555;
		margin-bottom: 16px;
	} 
	div.service-api div.types ul.list li.entry div.definition {
		font-size: 1.5em;
	} 
	div.service-api div.types ul.list li.entry div.definition span.name { color: #881a1a; } 
	div.service-api div.types ul.list li.entry span.param-type { color: #68387f; } 
	div.service-api div.types ul.list li.entry span.param-name {} 
	div.service-api div.types ul.list li.entry div.doc-lines { margin-top:0;margin-bottom:6px; font-size: 1.0em; color: #276d11; } 

	div.service-footer { font-size: 0.8em; text-align: center; font-style: italic; padding-top: 10px; padding-bottom: 10px; }

	a:link { color: #00732F; text-decoration: none }
	a:visited { color: #00732F; text-decoration: none }
	a:hover { color: #00732F; text-decoration: underline }
'''
