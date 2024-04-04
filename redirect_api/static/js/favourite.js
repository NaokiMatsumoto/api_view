$(document).ready(function() {
    function toggleFavorite() {
        var articleId = $(this).data('article-id');
        var button = $(this);
      
        sendToggleFavoriteRequest(articleId, button);
      }
      
      function sendToggleFavoriteRequest(articleId, button) {
        console.log('{{ csrf_token }}')
        $.ajax({
          url: '/news/toggle_favorite/' + articleId + '/',
          method: 'POST',
          data: {
            'csrfmiddlewaretoken': csrf_token,
          },
          success: function(response) {
            handleToggleFavoriteSuccess(response, button);
          },
          error: handleToggleFavoriteError
        });
      }
      
      function handleToggleFavoriteSuccess(response, button) {
        var icon = button.find('i');
        if (response.is_favorite) {
          icon.removeClass('text-muted').addClass('text-warning');
        } else {
          icon.removeClass('text-warning').addClass('text-muted');
        }
      }
      
      function handleToggleFavoriteError(xhr, status, error) {
        console.error(error);
      }
    $(document).ready(function() {
        $('.toggle-favorite').click(toggleFavorite);
    });
});