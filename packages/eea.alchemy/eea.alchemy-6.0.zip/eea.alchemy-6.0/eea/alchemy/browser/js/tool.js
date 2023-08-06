if(window.EEA === undefined){
  var EEA = {
    who: 'eea.alchemy',
    version: '5.0'
  };
}

if(!EEA.AlchemyDiscoverer){
  EEA.AlchemyDiscoverer = {
    version: '5.0'
  };
}

EEA.AlchemyDiscoverer.Events = {
  contentTypesChanged: 'eea-alchemy-content-type-changed',
  lookInChanged: 'eea-alchemy-lookin-changed',
  lookForChanged: 'eea-alchemy-lookfor-changed',
  batchChanged: 'eea-alchemy-batch-changed',
  formSubmit: 'eea-alchemy-form-submit',
  serverEvent: 'eea-alchemy-server-event'
};

EEA.AlchemyDiscoverer.ContentTypesBox = function(context, options){
  var self = this;
  self.context = context;

  self.settings = {
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AlchemyDiscoverer.ContentTypesBox.prototype = {
  initialize: function(){
    var self = this;
    self.filter = self.context.find('input[type="text"]');
    self.checkboxes = self.context.find('input[type="checkbox"]');

    self.context.fadeIn();

    // Handle events
    self.checkboxes.click(function(evt){
      var options = {};
      options.checked = jQuery(this).parents('.alchemy-box').find(':checked');
      options.element = jQuery(this);
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.contentTypesChanged, options);
    });

    self.filter.bind('input', function(){
      self.search(jQuery(this).val());
    });
  },

  search: function(text){
    var self = this;
    self.checkboxes.each(function(){
      var parent = jQuery(this).parents('li');
      var label = parent.find('label').text().toLowerCase();
      if(label.indexOf(text.toLowerCase()) === -1){
        parent.hide();
      }else{
        parent.show();
      }
    });
  }
};

EEA.AlchemyDiscoverer.LookInBox = function(context, options){
  var self = this;
  self.context = context;

  self.settings = {
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AlchemyDiscoverer.LookInBox.prototype = {
  initialize: function(){
    var self = this;
    self.filter = self.context.find('input[type="text"]');
    self.checkboxes = self.context.find('input[type="checkbox"]');

    // Handle events
    self.checkboxes.click(function(evt){
      var options = {};
      options.checked = jQuery(this).parents('.alchemy-box').find(':checked');
      options.element = jQuery(this);
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.lookInChanged, options);
    });

    self.filter.bind('input', function(){
      self.search(jQuery(this).val());
    });

    // Content-Type
    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.contentTypesChanged, function(evt, options){
      if(!options.checked.length){
        self.context.find(':checked').attr('checked', false);
        jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.lookInChanged, options);
        self.context.fadeOut();
      }else{
        self.context.fadeIn();
      }
    });
  },

  search: function(text){
    var self = this;
    self.checkboxes.each(function(){
      var parent = jQuery(this).parents('li');
      var label = parent.find('label').text().toLowerCase();
      if(label.indexOf(text.toLowerCase()) === -1){
        parent.hide();
      }else{
        parent.show();
      }
    });
  }
};

EEA.AlchemyDiscoverer.LookForBox = function(context, options){
  var self = this;
  self.context = context;

  self.settings = {
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AlchemyDiscoverer.LookForBox.prototype = {
  initialize: function(){
    var self = this;
    self.filter = self.context.find('input[type="text"]');
    self.checkboxes = self.context.find('input[type="checkbox"]');

    // Handle events
    self.checkboxes.click(function(evt, item){
      var options = {};
      options.checked = jQuery(this).parents('.alchemy-box').find(':checked');
      options.element = jQuery(this);
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.lookForChanged, options);
    });

    self.filter.bind('input', function(){
      self.search(jQuery(this).val());
    });

    // Look in
    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.lookInChanged, function(evt, options){
      if(!options.checked.length){
        self.context.find(':checked').attr('checked', false);
        jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.lookForChanged, options);
        self.context.fadeOut();
      }else{
        self.context.fadeIn();
      }
    });
  },

  search: function(text){
    var self = this;
    self.checkboxes.each(function(){
      var parent = jQuery(this).parents('li');
      var label = parent.find('label').text().toLowerCase();
      if(label.indexOf(text.toLowerCase()) === -1){
        parent.hide();
      }else{
        parent.show();
      }
    });
  }
};

EEA.AlchemyDiscoverer.BatchBox = function(context, options){
  var self = this;
  self.context = context;

  self.settings = {
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AlchemyDiscoverer.BatchBox.prototype = {
  initialize: function(){
    var self = this;
    self.form = self.context.parents('form');
    self.select = self.context.find('select');

    // Handle events

    // Look for
    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.lookForChanged, function(evt, options){
      if(!options.checked.length){
        self.context.fadeOut();
      }else{
        self.context.fadeIn();
      }
    });

    // Content-Type
    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.contentTypesChanged, function(evt, options){
      if(options.checked.length){
        self.updateBatch();
      }
    });
  },

  // Validate search form
  updateBatch: function(){
    var self = this;

    var action = '@@alchemy.batch';
    var query = self.form.serialize();
    jQuery.get(action, query, function(data){
      self.select.empty();

      var batch = 0;
      var batch_size = '';
      data = parseInt(data, 10);
      while(batch < data){
        if(batch + 300 < data){
          batch_size = batch + '-' + (batch + 300);
        }else{
          batch_size = batch + '-' + data;
        }

        jQuery('<option>').val(batch_size).text(batch_size).appendTo(self.select);
        batch = batch + 300;
      }
    });
  }
};

EEA.AlchemyDiscoverer.ConsoleBox = function(context, options){
  var self = this;
  self.context = context;
  self.console = self.context.find('.alchemy-console');

  self.settings = {
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AlchemyDiscoverer.ConsoleBox.prototype = {
  initialize: function(){
    var self = this;
    self.button = self.context.find('button');
    self.autoScroll = self.context.find('#auto-scrolling');

    // Handle events
    self.button.click(function(){
      self.clear();
    });

    // Look for
    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.lookForChanged, function(evt, options){
      if(!options.checked.length){
        self.context.fadeOut();
      }
    });

    // Form submit
    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.formSubmit, function(evt, options){
      self.context.fadeIn();
      self.info('Running: ' + options.action);
    });

    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.serverEvent, function(evt, options){
      self.log(options.data, options.type);
    });
  },

  info: function(msg){
    return this.log(msg, 'INFO');
  },

  error: function(msg){
    return this.log(msg, 'ERROR');
  },

  warn: function(msg){
    return this.log(msg, 'WARNING');
  },

  log: function(msg, level){
    var self = this;
    level = level || 'INFO';
    var output = jQuery('<p>')
      .addClass(level)
      .text(msg + "")
      .appendTo(self.console);

    if(self.autoScroll.attr('checked')){
      self.console.scrollTop(self.console[0].scrollHeight - self.console.height());
    }
  },

  clear: function(){
    return this.console.empty();
  }
};


EEA.AlchemyDiscoverer.Form = function(context, options){
  var self = this;
  self.context = context;

  self.settings = {
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AlchemyDiscoverer.Form.prototype = {
  initialize: function(){
    var self, boxes;

    self = this;
    self.form = self.context.find('form');
    self.buttons = jQuery('.alchemy-button', self.context);

    boxes = self.context.find('.alchemy-box');
    self.ctypes = new EEA.AlchemyDiscoverer.ContentTypesBox(jQuery(boxes[0]));
    self.lookin = new EEA.AlchemyDiscoverer.LookInBox(jQuery(boxes[1]));
    self.lookfor = new EEA.AlchemyDiscoverer.LookForBox(jQuery(boxes[2]));
    self.batch = new EEA.AlchemyDiscoverer.BatchBox(jQuery(boxes[3]));
    self.console = new EEA.AlchemyDiscoverer.ConsoleBox(jQuery(boxes[4]));

    // Events
    self.form.submit(function(evt){
      evt.preventDefault();
      return false;
    });

    self.buttons.find('input').click(function(evt){
      evt.preventDefault();
      var button = jQuery(this);
      return self.submit(button);
    });

    // Look For
    jQuery(document).bind(EEA.AlchemyDiscoverer.Events.lookForChanged, function(evt, options){
      if(!options.checked.length){
        self.buttons.fadeOut();
      }else{
        self.buttons.fadeIn();
      }
    });

    self.reload();
  },

  reload: function(){
    var self = this;
  },

  submit: function(button){
    var self = this;

    // Support old browsers
    if(!window.EventSource){
      return self.fallbackSubmit(button);
    }

    var query = self.form.serialize() + '&action=' + button.attr('value');
    var action = self.form.attr('action') + '?' + query;
    jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.formSubmit, {action: action});

    // Server-sent events
    self.setup();
    var sse = new EventSource(action);

    sse.addEventListener('INFO', function(message){
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.serverEvent, message);
    }, false);

    sse.addEventListener('WARNING', function(message){
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.serverEvent, message);
    }, false);

    sse.addEventListener('ERROR', function(message){
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.serverEvent, message);
    }, false);

    sse.addEventListener('CLOSE', function(message){
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.serverEvent, {
        data: message.data,
        type: 'INFO'
      });
      sse.close();
      self.cleanup();
    }, false);
  },

  fallbackSubmit: function(button){
    var self = this;
    jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.serverEvent, {
      data: ("!!! Your browser doesn't support Server-sent events, " +
             "therefore realtime logging will be disabled !!!"),
      type: 'WARNING'
    });

    var query = self.form.serialize() + '&action=' + button.attr('value');
    var action = self.form.attr('action');
    jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.formSubmit, {action: action + '?' + query});

    self.setup();
    jQuery.get(action, query, function(data){
      jQuery(document).trigger(EEA.AlchemyDiscoverer.Events.serverEvent, {
        data: data,
        type: 'INFO'
      });
      self.cleanup();
    });
  },

  setup: function(){
    var self = this;
    self.buttons.find('input').attr('disabled', true);
  },

  cleanup: function(){
    var self = this;
    self.buttons.find('input').removeClass('submitting');
    self.buttons.find('input').attr('disabled', false);
  }
};

jQuery.fn.EEAlchemyDiscoverer = function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new EEA.AlchemyDiscoverer.Form(context, options);
    context.data('EEAlchemyDiscoverer', adapter);
  });
};

// On document ready
jQuery(document).ready(function(){
  // Cleanup main template
  jQuery("#belowContent").remove();
  jQuery("#eea-comments").remove();
  jQuery(".discussion").remove();

  // Initialize
  jQuery('#eea-alchemy .alchemy-search').EEAlchemyDiscoverer();
});
