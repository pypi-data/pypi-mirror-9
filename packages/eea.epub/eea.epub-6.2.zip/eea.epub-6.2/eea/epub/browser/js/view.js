if(window.EEA === undefined){
  var EEA = {
    who: 'eea.epub',
    version: '6.0'
  };
}

EEA.ePub = function(context, options){
 var self = this;
  self.context = context;

  self.settings = {
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.ePub.prototype = {
  initialize: function(){
    var self = this;
    self.async = self.context.data('async');

    if(self.async){
      self.init_async();
    }

  },

  init_async: function(){
    var self = this;
    self.links = jQuery('body').find('a[href$="download.epub"]');

    self.links.prepOverlay({
      subtype: 'ajax',
      formselector: 'form',
      filter: '.eea-epub-download',
      cssclass: 'eea-epub-overlay'
    });
  }
};


jQuery.fn.EEAePub = function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new EEA.ePub(context, options);
    context.data('EEAePub', adapter);
  });
};

jQuery(document).ready(function(){

  var items = jQuery('.eea-epub-viewlet');
  items.EEAePub();

});
