/* CodeMirror - Minified & Bundled
   Generated on 11/9/2014 with http://codemirror.net/doc/compress.html
   Version: 4.5

   Modes:
   - xml.js
   Add-ons:
   - closetag.js
   - show-hint.js
   - xml-hint.js
 */

!function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],a):a(CodeMirror)}(function(a){"use strict";a.defineMode("xml",function(b,c){function k(a,b){function c(c){return b.tokenize=c,c(a,b)}var d=a.next();if("<"==d)return a.eat("!")?a.eat("[")?a.match("CDATA[")?c(n("atom","]]>")):null:a.match("--")?c(n("comment","-->")):a.match("DOCTYPE",!0,!0)?(a.eatWhile(/[\w\._\-]/),c(o(1))):null:a.eat("?")?(a.eatWhile(/[\w\._\-]/),b.tokenize=n("meta","?>"),"meta"):(i=a.eat("/")?"closeTag":"openTag",b.tokenize=l,"tag bracket");if("&"==d){var e;return e=a.eat("#")?a.eat("x")?a.eatWhile(/[a-fA-F\d]/)&&a.eat(";"):a.eatWhile(/[\d]/)&&a.eat(";"):a.eatWhile(/[\w\.\-:]/)&&a.eat(";"),e?"atom":"error"}return a.eatWhile(/[^&<]/),null}function l(a,b){var c=a.next();if(">"==c||"/"==c&&a.eat(">"))return b.tokenize=k,i=">"==c?"endTag":"selfcloseTag","tag bracket";if("="==c)return i="equals",null;if("<"==c){b.tokenize=k,b.state=s,b.tagName=b.tagStart=null;var d=b.tokenize(a,b);return d?d+" tag error":"tag error"}return/[\'\"]/.test(c)?(b.tokenize=m(c),b.stringStartCol=a.column(),b.tokenize(a,b)):(a.match(/^[^\s\u00a0=<>\"\']*[^\s\u00a0=<>\"\'\/]/),"word")}function m(a){var b=function(b,c){for(;!b.eol();)if(b.next()==a){c.tokenize=l;break}return"string"};return b.isInAttribute=!0,b}function n(a,b){return function(c,d){for(;!c.eol();){if(c.match(b)){d.tokenize=k;break}c.next()}return a}}function o(a){return function(b,c){for(var d;null!=(d=b.next());){if("<"==d)return c.tokenize=o(a+1),c.tokenize(b,c);if(">"==d){if(1==a){c.tokenize=k;break}return c.tokenize=o(a-1),c.tokenize(b,c)}}return"meta"}}function p(a,b,c){this.prev=a.context,this.tagName=b,this.indent=a.indented,this.startOfLine=c,(g.doNotIndent.hasOwnProperty(b)||a.context&&a.context.noIndent)&&(this.noIndent=!0)}function q(a){a.context&&(a.context=a.context.prev)}function r(a,b){for(var c;;){if(!a.context)return;if(c=a.context.tagName,!g.contextGrabbers.hasOwnProperty(c)||!g.contextGrabbers[c].hasOwnProperty(b))return;q(a)}}function s(a,b,c){return"openTag"==a?(c.tagStart=b.column(),t):"closeTag"==a?u:s}function t(a,b,c){return"word"==a?(c.tagName=b.current(),j="tag",x):(j="error",t)}function u(a,b,c){if("word"==a){var d=b.current();return c.context&&c.context.tagName!=d&&g.implicitlyClosed.hasOwnProperty(c.context.tagName)&&q(c),c.context&&c.context.tagName==d?(j="tag",v):(j="tag error",w)}return j="error",w}function v(a,b,c){return"endTag"!=a?(j="error",v):(q(c),s)}function w(a,b,c){return j="error",v(a,b,c)}function x(a,b,c){if("word"==a)return j="attribute",y;if("endTag"==a||"selfcloseTag"==a){var d=c.tagName,e=c.tagStart;return c.tagName=c.tagStart=null,"selfcloseTag"==a||g.autoSelfClosers.hasOwnProperty(d)?r(c,d):(r(c,d),c.context=new p(c,d,e==c.indented)),s}return j="error",x}function y(a,b,c){return"equals"==a?z:(g.allowMissing||(j="error"),x(a,b,c))}function z(a,b,c){return"string"==a?A:"word"==a&&g.allowUnquoted?(j="string",x):(j="error",x(a,b,c))}function A(a,b,c){return"string"==a?A:x(a,b,c)}var d=b.indentUnit,e=c.multilineTagIndentFactor||1,f=c.multilineTagIndentPastTag;null==f&&(f=!0);var i,j,g=c.htmlMode?{autoSelfClosers:{area:!0,base:!0,br:!0,col:!0,command:!0,embed:!0,frame:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0},implicitlyClosed:{dd:!0,li:!0,optgroup:!0,option:!0,p:!0,rp:!0,rt:!0,tbody:!0,td:!0,tfoot:!0,th:!0,tr:!0},contextGrabbers:{dd:{dd:!0,dt:!0},dt:{dd:!0,dt:!0},li:{li:!0},option:{option:!0,optgroup:!0},optgroup:{optgroup:!0},p:{address:!0,article:!0,aside:!0,blockquote:!0,dir:!0,div:!0,dl:!0,fieldset:!0,footer:!0,form:!0,h1:!0,h2:!0,h3:!0,h4:!0,h5:!0,h6:!0,header:!0,hgroup:!0,hr:!0,menu:!0,nav:!0,ol:!0,p:!0,pre:!0,section:!0,table:!0,ul:!0},rp:{rp:!0,rt:!0},rt:{rp:!0,rt:!0},tbody:{tbody:!0,tfoot:!0},td:{td:!0,th:!0},tfoot:{tbody:!0},th:{td:!0,th:!0},thead:{tbody:!0,tfoot:!0},tr:{tr:!0}},doNotIndent:{pre:!0},allowUnquoted:!0,allowMissing:!0,caseFold:!0}:{autoSelfClosers:{},implicitlyClosed:{},contextGrabbers:{},doNotIndent:{},allowUnquoted:!1,allowMissing:!1,caseFold:!1},h=c.alignCDATA;return{startState:function(){return{tokenize:k,state:s,indented:0,tagName:null,tagStart:null,context:null}},token:function(a,b){if(!b.tagName&&a.sol()&&(b.indented=a.indentation()),a.eatSpace())return null;i=null;var c=b.tokenize(a,b);return(c||i)&&"comment"!=c&&(j=null,b.state=b.state(i||c,a,b),j&&(c="error"==j?c+" error":j)),c},indent:function(b,c,i){var j=b.context;if(b.tokenize.isInAttribute)return b.tagStart==b.indented?b.stringStartCol+1:b.indented+d;if(j&&j.noIndent)return a.Pass;if(b.tokenize!=l&&b.tokenize!=k)return i?i.match(/^(\s*)/)[0].length:0;if(b.tagName)return f?b.tagStart+b.tagName.length+2:b.tagStart+d*e;if(h&&/<!\[CDATA\[/.test(c))return 0;var m=c&&/^<(\/)?([\w_:\.-]*)/.exec(c);if(m&&m[1])for(;j;){if(j.tagName==m[2]){j=j.prev;break}if(!g.implicitlyClosed.hasOwnProperty(j.tagName))break;j=j.prev}else if(m)for(;j;){var n=g.contextGrabbers[j.tagName];if(!n||!n.hasOwnProperty(m[2]))break;j=j.prev}for(;j&&!j.startOfLine;)j=j.prev;return j?j.indent+d:0},electricInput:/<\/[\s\w:]+>$/,blockCommentStart:"<!--",blockCommentEnd:"-->",configuration:c.htmlMode?"html":"xml",helperType:c.htmlMode?"html":"xml"}}),a.defineMIME("text/xml","xml"),a.defineMIME("application/xml","xml"),a.mimeModes.hasOwnProperty("text/html")||a.defineMIME("text/html",{name:"xml",htmlMode:!0})}),function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror"),require("../fold/xml-fold")):"function"==typeof define&&define.amd?define(["../../lib/codemirror","../fold/xml-fold"],a):a(CodeMirror)}(function(a){function d(d){if(d.getOption("disableInput"))return a.Pass;for(var e=d.listSelections(),h=[],i=0;i<e.length;i++){if(!e[i].empty())return a.Pass;var j=e[i].head,k=d.getTokenAt(j),l=a.innerMode(d.getMode(),k.state),m=l.state;if("xml"!=l.mode.name||!m.tagName)return a.Pass;var n=d.getOption("autoCloseTags"),o="html"==l.mode.configuration,p="object"==typeof n&&n.dontCloseTags||o&&b,q="object"==typeof n&&n.indentTags||o&&c,r=m.tagName;k.end>j.ch&&(r=r.slice(0,r.length-k.end+j.ch));var s=r.toLowerCase();if(!r||"string"==k.type&&(k.end!=j.ch||!/[\"\']/.test(k.string.charAt(k.string.length-1))||1==k.string.length)||"tag"==k.type&&"closeTag"==m.type||k.string.indexOf("/")==k.string.length-1||p&&f(p,s)>-1||g(d,r,j,m,!0))return a.Pass;var t=q&&f(q,s)>-1;h[i]={indent:t,text:">"+(t?"\n\n":"")+"</"+r+">",newPos:t?a.Pos(j.line+1,0):a.Pos(j.line,j.ch+1)}}for(var i=e.length-1;i>=0;i--){var u=h[i];d.replaceRange(u.text,e[i].head,e[i].anchor,"+insert");var v=d.listSelections().slice(0);v[i]={head:u.newPos,anchor:u.newPos},d.setSelections(v),u.indent&&(d.indentLine(u.newPos.line,null,!0),d.indentLine(u.newPos.line+1,null,!0))}}function e(b){if(b.getOption("disableInput"))return a.Pass;for(var c=b.listSelections(),d=[],e=0;e<c.length;e++){if(!c[e].empty())return a.Pass;var f=c[e].head,h=b.getTokenAt(f),i=a.innerMode(b.getMode(),h.state),j=i.state;if("string"==h.type||"<"!=h.string.charAt(0)||h.start!=f.ch-1||"xml"!=i.mode.name||!j.context||!j.context.tagName||g(b,j.context.tagName,f,j))return a.Pass;d[e]="/"+j.context.tagName+">"}b.replaceSelections(d),c=b.listSelections();for(var e=0;e<c.length;e++)(e==c.length-1||c[e].head.line<c[e+1].head.line)&&b.indentLine(c[e].head.line)}function f(a,b){if(a.indexOf)return a.indexOf(b);for(var c=0,d=a.length;d>c;++c)if(a[c]==b)return c;return-1}function g(b,c,d,e,f){if(!a.scanForClosingTag)return!1;var g=Math.min(b.lastLine()+1,d.line+500),h=a.scanForClosingTag(b,d,null,g);if(!h||h.tag!=c)return!1;for(var i=e.context,j=f?1:0;i&&i.tagName==c;i=i.prev)++j;d=h.to;for(var k=1;j>k;k++){var l=a.scanForClosingTag(b,d,null,g);if(!l||l.tag!=c)return!1;d=l.to}return!0}a.defineOption("autoCloseTags",!1,function(b,c,f){if(f!=a.Init&&f&&b.removeKeyMap("autoCloseTags"),c){var g={name:"autoCloseTags"};("object"!=typeof c||c.whenClosing)&&(g["'/'"]=function(a){return e(a)}),("object"!=typeof c||c.whenOpening)&&(g["'>'"]=function(a){return d(a)}),b.addKeyMap(g)}});var b=["area","base","br","col","command","embed","hr","img","input","keygen","link","meta","param","source","track","wbr"],c=["applet","blockquote","body","button","div","dl","fieldset","form","frameset","h1","h2","h3","h4","h5","h6","head","html","iframe","layer","legend","object","ol","p","select","table","ul"]}),function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],a):a(CodeMirror)}(function(a){"use strict";function d(a,b){this.cm=a,this.options=this.buildOptions(b),this.widget=this.onClose=null}function e(a){return"string"==typeof a?a:a.text}function f(a,b){function f(a,d){var f;f="string"!=typeof d?function(a){return d(a,b)}:c.hasOwnProperty(d)?c[d]:d,e[a]=f}var c={Up:function(){b.moveFocus(-1)},Down:function(){b.moveFocus(1)},PageUp:function(){b.moveFocus(-b.menuSize()+1,!0)},PageDown:function(){b.moveFocus(b.menuSize()-1,!0)},Home:function(){b.setFocus(0)},End:function(){b.setFocus(b.length-1)},Enter:b.pick,Tab:b.pick,Esc:b.close},d=a.options.customKeys,e=d?{}:c;if(d)for(var g in d)d.hasOwnProperty(g)&&f(g,d[g]);var h=a.options.extraKeys;if(h)for(var g in h)h.hasOwnProperty(g)&&f(g,h[g]);return e}function g(a,b){for(;b&&b!=a;){if("LI"===b.nodeName.toUpperCase()&&b.parentNode==a)return b;b=b.parentNode}}function h(d,h){this.completion=d,this.data=h;var i=this,j=d.cm,k=this.hints=document.createElement("ul");k.className="CodeMirror-hints",this.selectedHint=h.selectedHint||0;for(var l=h.list,m=0;m<l.length;++m){var n=k.appendChild(document.createElement("li")),o=l[m],p=b+(m!=this.selectedHint?"":" "+c);null!=o.className&&(p=o.className+" "+p),n.className=p,o.render?o.render(n,h,o):n.appendChild(document.createTextNode(o.displayText||e(o))),n.hintId=m}var q=j.cursorCoords(d.options.alignWithWord?h.from:null),r=q.left,s=q.bottom,t=!0;k.style.left=r+"px",k.style.top=s+"px";var u=window.innerWidth||Math.max(document.body.offsetWidth,document.documentElement.offsetWidth),v=window.innerHeight||Math.max(document.body.offsetHeight,document.documentElement.offsetHeight);(d.options.container||document.body).appendChild(k);var w=k.getBoundingClientRect(),x=w.bottom-v;if(x>0){var y=w.bottom-w.top,z=q.top-(q.bottom-w.top);if(z-y>0)k.style.top=(s=q.top-y)+"px",t=!1;else if(y>v){k.style.height=v-5+"px",k.style.top=(s=q.bottom-w.top)+"px";var A=j.getCursor();h.from.ch!=A.ch&&(q=j.cursorCoords(A),k.style.left=(r=q.left)+"px",w=k.getBoundingClientRect())}}var B=w.left-u;if(B>0&&(w.right-w.left>u&&(k.style.width=u-5+"px",B-=w.right-w.left-u),k.style.left=(r=q.left-B)+"px"),j.addKeyMap(this.keyMap=f(d,{moveFocus:function(a,b){i.changeActive(i.selectedHint+a,b)},setFocus:function(a){i.changeActive(a)},menuSize:function(){return i.screenAmount()},length:l.length,close:function(){d.close()},pick:function(){i.pick()},data:h})),d.options.closeOnUnfocus){var C;j.on("blur",this.onBlur=function(){C=setTimeout(function(){d.close()},100)}),j.on("focus",this.onFocus=function(){clearTimeout(C)})}var D=j.getScrollInfo();return j.on("scroll",this.onScroll=function(){var a=j.getScrollInfo(),b=j.getWrapperElement().getBoundingClientRect(),c=s+D.top-a.top,e=c-(window.pageYOffset||(document.documentElement||document.body).scrollTop);return t||(e+=k.offsetHeight),e<=b.top||e>=b.bottom?d.close():(k.style.top=c+"px",k.style.left=r+D.left-a.left+"px",void 0)}),a.on(k,"dblclick",function(a){var b=g(k,a.target||a.srcElement);b&&null!=b.hintId&&(i.changeActive(b.hintId),i.pick())}),a.on(k,"click",function(a){var b=g(k,a.target||a.srcElement);b&&null!=b.hintId&&(i.changeActive(b.hintId),d.options.completeOnSingleClick&&i.pick())}),a.on(k,"mousedown",function(){setTimeout(function(){j.focus()},20)}),a.signal(h,"select",l[0],k.firstChild),!0}var b="CodeMirror-hint",c="CodeMirror-hint-active";a.showHint=function(a,b,c){if(!b)return a.showHint(c);c&&c.async&&(b.async=!0);var d={hint:b};if(c)for(var e in c)d[e]=c[e];return a.showHint(d)},a.defineExtension("showHint",function(b){if(!(this.listSelections().length>1||this.somethingSelected())){this.state.completionActive&&this.state.completionActive.close();var c=this.state.completionActive=new d(this,b),e=c.options.hint;if(e)return a.signal(this,"startCompletion",this),e.async?(e(this,function(a){c.showHints(a)},c.options),void 0):c.showHints(e(this,c.options))}}),d.prototype={close:function(){this.active()&&(this.cm.state.completionActive=null,this.widget&&this.widget.close(),this.onClose&&this.onClose(),a.signal(this.cm,"endCompletion",this.cm))},active:function(){return this.cm.state.completionActive==this},pick:function(b,c){var d=b.list[c];d.hint?d.hint(this.cm,b,d):this.cm.replaceRange(e(d),d.from||b.from,d.to||b.to,"complete"),a.signal(b,"pick",d),this.close()},showHints:function(a){return a&&a.list.length&&this.active()?(this.options.completeSingle&&1==a.list.length?this.pick(a,0):this.showWidget(a),void 0):this.close()},showWidget:function(b){function l(){e||(e=!0,d.close(),d.cm.off("cursorActivity",p),b&&a.signal(b,"close"))}function m(){if(!e){a.signal(b,"update");var c=d.options.hint;c.async?c(d.cm,n,d.options):n(c(d.cm,d.options))}}function n(a){if(b=a,!e){if(!b||!b.list.length)return l();d.widget&&d.widget.close(),d.widget=new h(d,b)}}function o(){c&&(k(c),c=0)}function p(){o();var a=d.cm.getCursor(),b=d.cm.getLine(a.line);a.line!=g.line||b.length-a.ch!=i-g.ch||a.ch<g.ch||d.cm.somethingSelected()||a.ch&&f.test(b.charAt(a.ch-1))?d.close():(c=j(m),d.widget&&d.widget.close())}this.widget=new h(this,b),a.signal(b,"shown");var e,c=0,d=this,f=this.options.closeCharacters,g=this.cm.getCursor(),i=this.cm.getLine(g.line).length,j=window.requestAnimationFrame||function(a){return setTimeout(a,1e3/60)},k=window.cancelAnimationFrame||clearTimeout;this.cm.on("cursorActivity",p),this.onClose=l},buildOptions:function(a){var b=this.cm.options.hintOptions,c={};for(var d in i)c[d]=i[d];if(b)for(var d in b)void 0!==b[d]&&(c[d]=b[d]);if(a)for(var d in a)void 0!==a[d]&&(c[d]=a[d]);return c}},h.prototype={close:function(){if(this.completion.widget==this){this.completion.widget=null,this.hints.parentNode.removeChild(this.hints),this.completion.cm.removeKeyMap(this.keyMap);var a=this.completion.cm;this.completion.options.closeOnUnfocus&&(a.off("blur",this.onBlur),a.off("focus",this.onFocus)),a.off("scroll",this.onScroll)}},pick:function(){this.completion.pick(this.data,this.selectedHint)},changeActive:function(b,d){if(b>=this.data.list.length?b=d?this.data.list.length-1:0:0>b&&(b=d?0:this.data.list.length-1),this.selectedHint!=b){var e=this.hints.childNodes[this.selectedHint];e.className=e.className.replace(" "+c,""),e=this.hints.childNodes[this.selectedHint=b],e.className+=" "+c,e.offsetTop<this.hints.scrollTop?this.hints.scrollTop=e.offsetTop-3:e.offsetTop+e.offsetHeight>this.hints.scrollTop+this.hints.clientHeight&&(this.hints.scrollTop=e.offsetTop+e.offsetHeight-this.hints.clientHeight+3),a.signal(this.data,"select",this.data.list[this.selectedHint],e)}},screenAmount:function(){return Math.floor(this.hints.clientHeight/this.hints.firstChild.offsetHeight)||1}},a.registerHelper("hint","auto",function(b,c){var e,d=b.getHelpers(b.getCursor(),"hint");if(d.length)for(var f=0;f<d.length;f++){var g=d[f](b,c);if(g&&g.list.length)return g}else if(e=b.getHelper(b.getCursor(),"hintWords")){if(e)return a.hint.fromList(b,{words:e})}else if(a.hint.anyword)return a.hint.anyword(b,c)}),a.registerHelper("hint","fromList",function(b,c){for(var d=b.getCursor(),e=b.getTokenAt(d),f=[],g=0;g<c.words.length;g++){var h=c.words[g];h.slice(0,e.string.length)==e.string&&f.push(h)}return f.length?{list:f,from:a.Pos(d.line,e.start),to:a.Pos(d.line,e.end)}:void 0}),a.commands.autocomplete=a.showHint;var i={hint:a.hint.auto,completeSingle:!0,alignWithWord:!0,closeCharacters:/[\s()\[\]{};:>,]/,closeOnUnfocus:!0,completeOnSingleClick:!1,container:null,customKeys:null,extraKeys:null};a.defineOption("hintOptions",null)}),function(a){"object"==typeof exports&&"object"==typeof module?a(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],a):a(CodeMirror)}(function(a){"use strict";function c(c,d){var e=d&&d.schemaInfo,f=d&&d.quoteChar||'"';if(e){var g=c.getCursor(),h=c.getTokenAt(g),i=a.innerMode(c.getMode(),h.state);if("xml"==i.mode.name){var l,o,j=[],k=!1,m=/\btag\b/.test(h.type),n=m&&/^\w/.test(h.string);if(n){var p=c.getLine(g.line).slice(Math.max(0,h.start-2),h.start),q=/<\/$/.test(p)?"close":/<$/.test(p)?"open":null;q&&(o=h.start-("close"==q?2:1))}else m&&"<"==h.string?q="open":m&&"</"==h.string&&(q="close");if(!m&&!i.state.tagName||q){n&&(l=h.string),k=q;var r=i.state.context,s=r&&e[r.tagName],t=r?s&&s.children:e["!top"];if(t&&"close"!=q)for(var u=0;u<t.length;++u)l&&0!=t[u].lastIndexOf(l,0)||j.push("<"+t[u]);else if("close"!=q)for(var v in e)!e.hasOwnProperty(v)||"!top"==v||"!attrs"==v||l&&0!=v.lastIndexOf(l,0)||j.push("<"+v);r&&(!l||"close"==q&&0==r.tagName.lastIndexOf(l,0))&&j.push("</"+r.tagName+">")}else{var s=e[i.state.tagName],w=s&&s.attrs,x=e["!attrs"];if(!w&&!x)return;if(w){if(x){var y={};for(var z in x)x.hasOwnProperty(z)&&(y[z]=x[z]);for(var z in w)w.hasOwnProperty(z)&&(y[z]=w[z]);w=y}}else w=x;if("string"==h.type||"="==h.string){var B,p=c.getRange(b(g.line,Math.max(0,g.ch-60)),b(g.line,"string"==h.type?h.start:h.end)),A=p.match(/([^\s\u00a0=<>\"\']+)=$/);if(!A||!w.hasOwnProperty(A[1])||!(B=w[A[1]]))return;if("function"==typeof B&&(B=B.call(this,c)),"string"==h.type){l=h.string;var C=0;/['"]/.test(h.string.charAt(0))&&(f=h.string.charAt(0),l=h.string.slice(1),C++);var D=h.string.length;/['"]/.test(h.string.charAt(D-1))&&(f=h.string.charAt(D-1),l=h.string.substr(C,D-2)),k=!0}for(var u=0;u<B.length;++u)l&&0!=B[u].lastIndexOf(l,0)||j.push(f+B[u]+f)}else{"attribute"==h.type&&(l=h.string,k=!0);for(var E in w)!w.hasOwnProperty(E)||l&&0!=E.lastIndexOf(l,0)||j.push(E)}}return{list:j,from:k?b(g.line,null==o?h.start:o):g,to:k?b(g.line,h.end):g}}}}var b=a.Pos;a.registerHelper("hint","xml",c)});


// ============================================================================


/*global jQuery: true */
/*global setTimeout: true */
/*global CodeMirror: true */
/*global tags: true */

// ----------------------------------------------------------------------------
function schema2tags(schema, top) {
    var tags = {"!top": top};
    var element;

    for (var pattern in schema) {
        if (pattern.indexOf(".") == 0)
            continue;
        element = schema[pattern].element || pattern;
        if (element.indexOf(".") != -1)
            continue;
        if (!tags[element])
            tags[element] = {};

        if (schema[pattern].attributes) {
            if (!tags[element].attrs)
                tags[element].attrs = schema[pattern].attributes;
            else
                jQuery.extend(tags[element].attrs, schema[pattern].attributes);
        }

        if (!tags[element].children)
            tags[element].children = [];
        if (!schema[pattern].content)
            continue;

        for (var i = 0 ; i < schema[pattern].content.length ; i++)
            for (var elt, j = 0; j < schema[pattern].content[i].length; j++) {
                elt = schema[schema[pattern].content[i][j]] &&
                    schema[schema[pattern].content[i][j]].element
                    || schema[pattern].content[i][j];
                if (elt.indexOf(".") == -1
                    && jQuery.inArray(elt, tags[element].children) == -1)
                    tags[element].children.push(elt);
            }
    }

    return tags;
}

// ----------------------------------------------------------------------------
function completeAfter(cm, pred) {
    var cur = cm.getCursor();
    if (!pred || pred()) setTimeout(function() {
        if (!cm.state.completionActive)
            CodeMirror.showHint(
                cm, CodeMirror.xmlHint,
                { schemaInfo: tags, completeSingle: false}
            );
    }, 100);
    return CodeMirror.Pass;
}

// ----------------------------------------------------------------------------
function completeIfAfterLt(cm) {
    return completeAfter(cm, function() {
        var cur = cm.getCursor();
        return cm.getRange(CodeMirror.Pos(cur.line, cur.ch - 1), cur) == "<";
    });
}

// ----------------------------------------------------------------------------
function completeIfInTag(cm) {
    return completeAfter(cm, function() {
        var tok = cm.getTokenAt(cm.getCursor());
        if (tok.type == "string"
            && (!/['"]/.test(tok.string.charAt(tok.string.length - 1))
                || tok.string.length == 1))
            return false;
        var inner = CodeMirror.innerMode(cm.getMode(), tok.state).state;
        return inner.tagName;
    });
}

// ----------------------------------------------------------------------------
function metaHideEmptyFields($metaTable) {
    // Find empty fields
    var fields = [];
    $metaTable.find("input[type='text'], textarea, select").each(function() {
        var $this = jQuery(this);
        if (!jQuery.trim($this.val())) {
            var $tr = $this.parents("tr");
            fields.push([
                $tr.prevAll("tr").length, $tr.children("td").eq(0).text()]);
            $tr.hide();
        }
    });
    if (!(fields.length))
        return;

    // Hide and connect
    var $newTag = "<option/>";
    for (var i = 0 ; i < fields.length ; i++)
        $newTag += "<option value='" + fields[i][0] + "'>"
        + fields[i][1] + "</option>";
    $newTag = jQuery(
        "<tr><td><select>"+$newTag+"</select></td><td colspan='2'/></tr>");
    $newTag.find("select").change(function() {
        var $select = jQuery(this);
        $metaTable.find("tr").eq($select.val()).show()
            .find("input").eq(0).focus();
        $select.children("option[value='"+ $select.val() + "']").remove();
        if ($select.children("option").length < 2)
            $select.parents("tr").remove();
        else
            $select.val('');
    });
    $metaTable.append($newTag);
}
