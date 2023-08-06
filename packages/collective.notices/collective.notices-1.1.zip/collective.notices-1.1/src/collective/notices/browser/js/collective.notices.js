var dummy = function($) {

function attachNoticeCloseLink() {
  $('a.notice-action-hide').click(function(event){
    var link = $(event.target);

    // notify server
    $.ajax({
      'url': link.attr('href'),
      'type': 'get',
      'dataType': 'html',
      'data': {'ajax': '1'},
      'async': true,
      'success': function(data, status, xhr) {
        if (status != 'success') {
          alert('Sorry, something went wrong on the server. Please, try ' +
            'again a bit later.');
          return false;
        }
        
        // remove notice
        link.parents('.notice').remove();
        
        return true;
      },
      'error': function(data, xhr) {
        alert('Sorry, something went wrong on the server. Please, try ' +
          'again a bit later.');
        return false;
      }
    });
    
    return false;
  });
};

// page load handler
$(function(){
  attachNoticeCloseLink();
});

}(jQuery);

delete dummy;
