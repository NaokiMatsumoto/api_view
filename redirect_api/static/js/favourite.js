function toggleCommentSection(commentIcon) {
  var articleId = commentIcon.data('article-id');
  var commentSection = $('.comment-section[comment-article-id="' + articleId + '"]');
  if (commentSection.hasClass('show')) {
      hideCommentSection(articleId);
  } else {
      showCommentSection(articleId);
  }
}

function showCommentSection(articleId) {
  var commentSection = $('.comment-section[comment-article-id="' + articleId + '"]');
  var favoriteItem = $('.favorite-item[data-article-id="' + articleId + '"]');

  $('.comment-section.show').removeClass('show');
  commentSection.css({
      position: 'absolute',
      top: favoriteItem.outerHeight() / 2,
      right: 0,
      width: favoriteItem.outerWidth() * 2 / 3,
  }).addClass('show');
}

function hideCommentSection(articleId) {
  var commentSection = $('.comment-section[comment-article-id="' + articleId + '"]');
  var favoriteItem = $('.favorite-item[data-article-id="' + articleId + '"]');
  commentSection.removeClass('show');
  setTimeout(function() {
      commentSection.css({
        top: favoriteItem.outerHeight() / 2,
        right: 0,
        width: favoriteList.outerWidth() * 2 / 3,
      });
  }, 300);
}

function saveComment(articleId, content) {
  $.ajax({
      url: '/news/comment/' + articleId + '/',
      method: 'POST',
      data: {
          'content': content,
          'csrfmiddlewaretoken': csrf_token
      },
      success: function(response) {
        if (content !== '') {
          var commentIcon = $('.comment-icon[data-article-id="' + articleId + '"]');
          if (!commentIcon.find('.fa-comment').hasClass('text-primary')) {
            commentIcon.html('<i class="fas fa-comment text-primary"></i>');
          }
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
          console.error("Error in Ajax request:", textStatus, errorThrown);
      } 
  });
}

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
    
    $(document).on('click', '.comment-icon', function(e) {
        e.stopPropagation();
        toggleCommentSection($(this));
    });
    $('.save-comment').on('click', function() {
      var articleId = $(this).data('article-id');
      var content = $(this).closest('.comment-form').find('.comment-textarea').val();
      saveComment(articleId, content);
      hideCommentSection(articleId);
    });
});