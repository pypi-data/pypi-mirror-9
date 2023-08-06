var overlay_id = 'pb_99938783';
var overlay_selector = '#' + overlay_id;
var overlay_content_selector = overlay_selector + ' .pb-ajax .overlaycontent';
var content_selector = overlay_content_selector;
var selected_checkbox = null;

$('body').append('' +
  '<div id="' + overlay_id + '" class="overlay overlay-ajax "' +
       'style="width: 90%">' +
    '<div class="close"><span>Close</span></div>' +
    '<div class="pb-ajax">' +
      '<div class="overlaycontent"></div>' +
    '</div>' +
  '</div>');

$(overlay_selector).overlay({
  onClose : function(){
    $(overlay_content_selector).html('');//clear it
  }
});


var Form = function(data){
  var self = this;
  /* load overlay */
  self.$wrap = $(overlay_content_selector);
  self.$wrap.html(data);

  self.init = function(){
    self.ed = tinyMCE.activeEditor;
    self.item = self.ed.selection.getNode();
    self.$item = $(self.item);
    self.checkTimeout = null;

    /* check for existing iframe */
    var $iframe = [];
    if(self.$item.hasClass('mceItemIframe')){
      $iframe = self.$item;
    }else{
      $iframe = self.$item.find('.mceItemIframe');
    }
    if($iframe.length > 0){
      // need to convert back to normal url
      var data = tinymce.util.JSON.parse($iframe.attr('data-mce-json'));
      var url = data.params.src;
      if(url.indexOf('www.youtube') !== -1){
        var id = url.split('/embed/')[1].split('?')[0];
        var youtubeurl = 'http://www.youtube.com/watch?v=' + id;
        self.set('url', youtubeurl);
        self.set('width', $iframe.attr('width'));
        self.set('height', $iframe.attr('height'));
        self.set('privacymode', url.indexOf('nocookie.com') !== -1);
        self.set('autohide', url.indexOf('autohide=1') !== -1);
        self.set('showinfo', url.indexOf('showinfo=0') === -1);
        self.set('modestbranding', url.indexOf('modestbranding=1') !== -1);
        self.showPreview();
      }
    }

    self.$wrap.find('button.insert').click(function(e){
      e.preventDefault();
      var $el = self.getTinyEl();
      if($el){
        if(self.$item.hasClass('mceItemIframe')){
          self.$item.replaceWith($el);
        }else{
          self.$item.empty();
          self.$item.append($el);
        }
        $(overlay_selector).overlay().close();
      }else{
        alert('not a valid youtube url detected');
      }
      return false;
    });
    self.$wrap.find('button.cancel').click(function(e){
      e.preventDefault();
      $(overlay_selector).overlay().close();
      return false;
    });
    var check = function(){
      /* after clicks check if we can show a preview */
      if(self.checkTimeout !== null){
        clearTimeout(self.checkTimeout);
      }
      self.checkTimeout = setTimeout(function(){
        self.showPreview();
      }, 700);
    };

    self.$wrap.find('input[type="text"]').keyup(check);
    self.$wrap.find('input[type="checkbox"]').change(check);
  };

  self.get = function(name){
    // get value from form
    var $el = self.$wrap.find('#youtube' + name);
    if($el.length > 0){
      if($el.attr('type') === 'checkbox'){
        return $el[0].checked;
      }else{
        return $el.val();
      }
    }
  };

  self.set = function(name, val){
    // set value from form
    var $el = self.$wrap.find('#youtube' + name);
    if($el.length > 0){
      if($el.attr('type') === 'checkbox'){
        if(val){
          $el[0].checked = true;
        }else{
          $el[0].checked = false;
        }
      }else{
        $el.val(val);
      }
    }
  };

  self.getOptions = function(){
    var query = '?fs=1&amp;wmode=transparent&amp;rel=0&amp;html5=1';
    if(self.get('autohide')){
      query += '&amp;autohide=1';
    }
    if(!self.get('showinfo')){
      query += '&amp;showinfo=0';
    }
    if(self.get('modestbranding')){
      query += '&amp;modestbranding=1';
    }

    var url = self.get('url');
    var id = url.split('v=')[1];
    if(id){
      id = id.split('&')[0]; // trim more off
      var base_url = '//www.youtube.com/embed/';
      if(self.get('privacymode')){
        base_url = '//www.youtube-nocookie.com/embed/';
      }
      url = base_url + id + query;
    }else{
      url = null;
    }

    return {
      width: parseInt(self.get('width')),
      height: parseInt(self.get('height')),
      url: url
    };
  };

  self.showPreview = function(){
    self.$wrap.find('.preview .container').empty().html(self.getMarkup());
  };

  self.getMarkup = function(){
    var options = self.getOptions();
    if(options.url === null){
      return '<span />';
    }
    return '<iframe width="' + options.width + '" height="' + options.height + '" ' +
                    'src="' + options.url + '" frameborder="0" allowfullscreen></iframe>';
  };

  self.getTinyEl = function(){
    var options = self.getOptions();
    if(options.url === null){
      return null;
    }
    var data = {
      'video': {},
      'params': {
        'src': options.url,
        'frameborder': '0',
        'allowfullscreen': ''
      },
      'hspace':null,
      'vspace':null,
      'align':null,
      'bgcolor':null
    };
    var $el = $('' +
      '<img src="themes/advanced/img/trans.gif" width="' + options.width + '"' +
      '     height="' + options.height + '" class="mceItemMedia mceItemIframe" >');

    $el.attr('data-mce-json', tinymce.util.JSON.serialize(data));
    return $el;
  };

  self.init();
  return self;
};


function loadOverlay(){
  $('#kss-spinner').show();
  $.ajax({
    url : $('base').attr('href') + '/add-tinymce-youtube',
    success: function(data, textStatus, req){
      var form = new Form(data);
      $('#kss-spinner').hide();
    }
  });
  $(overlay_selector).overlay().load();
}


(function() {
  tinymce.create('tinymce.plugins.TMCEYoutubePlugin', {
    init : function(ed, url) {
      // Register the command so that it can be invoked by using tinyMCE.activeEditor.execCommand('mceExample');
      ed.addCommand('tmceyoutube', function() {
        try{
          loadOverlay();
        }catch(e){
          alert('Whoops. Something went wrong loading youtube form. \n' + e);
        }
      });

      // Register example button
      ed.addButton('tmceyoutube', {
        title : 'Add/Edit youtube video',
        cmd : 'tmceyoutube',
        image : url + '/youtube.png'
      });
    }

  });

  tinymce.PluginManager.add('tmceyoutube', tinymce.plugins.TMCEYoutubePlugin);
})();
