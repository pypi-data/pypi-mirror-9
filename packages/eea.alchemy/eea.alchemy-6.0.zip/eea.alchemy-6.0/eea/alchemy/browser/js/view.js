if (typeof String.prototype.endswith !== 'function') {
  String.prototype.endswith = function(suffix) {
      return this.indexOf(suffix, this.length - suffix.length) !== -1;
  };
}

if(window.EEA === undefined){
  var EEA = {
    who: 'eea.alchemy',
    version: '5.0'
  };
}

EEA.Highlighter = function(context, options){
 var self = this;
  self.context = context;

  self.settings = {
    highlightClass: 'eea-alchemy-tag',
    caseInsensitive: true
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.Highlighter.prototype = {
  initialize: function(){
    var self = this;
    self.highlight(self.context);
  },

  highlight: function(startnode) {
    var self = this;
    if(!startnode.length){
      return;
    }

    jQuery.each(self.settings.search, function(key, value) {
      startnode.find('*:not(textarea)').andSelf().contents().each(function() {
        if (this.nodeType === 3) {
          self.highlightTermInNode(this, key, value);
        }
      });
    });
  },

  highlightTermInNode: function(node, word, link){
    var self = this;
    var highlight, index, next;
    var c = node.nodeValue;

    var s1 = '\\s[\\"\\{\\[\\(]?';
    var s2 = '[\\"\\}\\]\\)\\.\\,\\!\\?\\;\\:\\s]';
    var search = new RegExp(s1 + word + s2, 'gi');

    // Highlight
    highlight = function(content, word, url) {
      return jQuery('<span class="' + self.settings.highlightClass + '" data-word="' + word + '" data-url="' + url + word + '">' + content + '</span>');
    };

    while (c && c.search(search) > -1) {
        // replace the node with [before]<span>word</span>[after]
        index = c.toLowerCase().indexOf(word.toLowerCase());
        jQuery(node)
            .before(document.createTextNode(c.substr(0, index)))
            .before(highlight(c.substr(index, word.length), word, link))
            .before(document.createTextNode(c.substr(index+word.length)));
        next = node.previousSibling; // text after the a
        jQuery(node).remove();
        // wash, rinse and repeat
        node = next;
        c = node.nodeValue;
    }
  }
};

EEA.Alchemy = function(context, options){
  var self = this;
  self.context = context;

  self.settings = {
    api: 'alchemy.tags.json',
    highlightClass: 'eea-alchemy-tag'
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  try{
    self.initialize();
  }catch(err){
    if(window.console){
      console.log(err);
    }
  }
};

EEA.Alchemy.prototype = {
  initialize: function(){
    var self = this;
    jQuery.ajax({
      dataType: "json",
      url: self.settings.api,
      success: function(data){
        self.onSuccess(data);
      }
    });
  },

  onSuccess: function(options){
    var self = this;

    // Auto-tagging is not enabled
    if(!options.enabled){
      return;
    }

    // Nothing to search
    if(!options.search){
      return;
    }

    if(options.modal){
      self.makeModal();
    }

    jQuery.extend(self.settings, options);
    return self.reload();
  },

  reload: function(){
    var self = this;
    self.exists = {};
    var adapter = new EEA.Highlighter(self.context, self.settings);
    self.context.data('EEAHighlighter', adapter);
    jQuery('.' + self.settings.highlightClass, self.context).each(function(){
      return self.reloadItem(jQuery(this));
    });
  },

  reloadItem: function(item){
    var self = this;

    // Skip blacklisted items
    var blacklist = self.settings.blacklist || [];
    blacklist.push('a');
    blacklist = blacklist.join(',');

    if(item.parents(blacklist).length){
      item.removeClass(self.settings.highlightClass);
      return;
    }

    var url = item.data('url');
    if(!url){
      return;
    }

    // Handle Highlight firstOnly option
    var word = item.data('word');
    if(self.settings.firstOnly && self.exists[word.toLowerCase()]){
      item.removeClass(self.settings.highlightClass);
      return;
    }
    self.exists[word.toLowerCase()] = url;

    // Add link
    var link = jQuery('<a>')
      .attr('href', url)
      .text(item.text());
    item.html(link);
    item.show('highlight', 2000);
  },

  makeModal: function(){

  }
};

jQuery.fn.EEAlchemy = function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new EEA.Alchemy(context, options);
    context.data('EEAlchemy', adapter);
  });
};

// On document ready
jQuery(document).ready(function(){
  var enabled = jQuery('#eea-alchemy-enabled');
  if(!enabled.length){
    return;
  }

  var items = jQuery('#region-content,#content');
  if(!items.length){
    return;
  }

  // Skip edit forms
  var href = window.location.href.split('?')[0];
  if(href.endswith('edit')){
    return;
  }

  if(items.find('[name="edit_form"]').length){
    return;
  }

  // Compute base link
  base = jQuery('base').attr('href') || '';

  if(base && base.endswith('/view')){
    base = base.replace(/\/view$/g, '/');
  }

  if(base && !base.endswith('/')){
    base += '/';
  }

  items.EEAlchemy({
    api: base + 'alchemy.tags.json'
  });

  var modal = jQuery('#eea-alchemy-modalEnabled');
  if (modal.length){
    jQuery("body").delegate(".eea-alchemy-tag a", "click", function() {
      jQuery("#eea-alchemy-modal-output").remove();
      jQuery("body").append(jQuery("<div id='eea-alchemy-modal-output'></div>"));
      var url = encodeURI(jQuery(this).attr("href").replace("@@search", "@@updated_search"));
      jQuery("#eea-alchemy-modal-output").dialog({
        width:800,
        height:600,
        modal:true,
        title:"Results",
        open: function(evt, ui){
          jQuery("#eea-alchemy-modal-output").load(url);
        }
      });
      return false;
    });

    jQuery("body").delegate("#eea-alchemy-modal-output #updated-sorting-options a", "click", function() {
      var url = jQuery(this).attr("href").replace("@@search", "@@updated_search");
      jQuery("#eea-alchemy-modal-output").html("");
      jQuery("#eea-alchemy-modal-output").load(url);
      return false;
    });

    jQuery("body").delegate("#eea-alchemy-modal-output .listingBar a", "click", function() {
      var url = jQuery(this).attr("href");
      jQuery("#eea-alchemy-modal-output").html("");
      jQuery("#eea-alchemy-modal-output").load(url);
      return false;
    });
  }
});
