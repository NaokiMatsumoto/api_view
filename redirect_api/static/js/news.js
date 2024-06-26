function deleteComment(articleId) {
    $.ajax({
        url: '/news/comment/delete/' + articleId + '/',
        method: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function(response) {
            console.log("Success callback executed");
            if (response.success) {
                console.log("Response success is true");
                // コメントを削除
                var commentSection = $('.comment-section[comment-article-id="' + articleId + '"]');
                var commentTextarea = commentSection.find('.comment-textarea');
                commentTextarea.val('');
                commentSection.find('.delete-comment').remove();
                commentSection.find('.save-comment').text('保存');
            } 
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Error in Ajax request:", textStatus, errorThrown);
        }    
    });
}

function initDatePicker() {
    $('#datePicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true
    }).on('changeDate', function(e) {
        var selectedDate = e.format();
        var [year, month, day] = selectedDate.split('-');
        window.location.href = `/news/${year}/${month}/${day}/`;
    });
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
    var articleList = $('.article-item[data-article-id="' + articleId + '"]');

    $('.comment-section.show').removeClass('show');
    commentSection.css({
        position: 'absolute',
        top: articleList.outerHeight(),
        right: 0,
        width: articleList.outerWidth() * 2 / 3,
    }).addClass('show');
}

function hideCommentSection(articleId) {
    var commentSection = $('.comment-section[comment-article-id="' + articleId + '"]');
    var articleList = $('.article-item[data-article-id="' + articleId + '"]');

    commentSection.removeClass('show');
    setTimeout(function() {
        commentSection.css({
            top: articleList.outerHeight(),
            right: 0,
            width: articleList.outerWidth() * 2 / 3,
        });
    }, 300);
}

$(document).ready(function() {
    var hideButton = $('#hideButton');
    var checkboxes = $('input[type="checkbox"]');
    var hideForm = $('#hideForm');
    
    function updateHideButtonVisibility() {
        var checkedCount = checkboxes.filter(':checked').length;
        hideButton.toggleClass('show', checkedCount > 0);
    }

    
    function handleCheckboxClick(e) {
        if ($(e.target).is('a')) {
            return;
        }
        e.preventDefault();
        var checkbox = $(this);
        checkbox.prop('checked', !checkbox.is(':checked')).attr('value', checkbox.is(':checked'));
        updateHideButtonVisibility();
    }

    function handleHideFormSubmit(event) {
        event.preventDefault();
        var selectedArticleIds = checkboxes.filter(':checked').map(function() {
            return $(this).data('article-id');
        }).get();

        $('<input>').attr({
            type: 'hidden',
            name: 'article_ids',
            value: selectedArticleIds.join(',')
        }).appendTo(hideForm);

        hideForm.off('submit').submit();
    }

    function getClickedLinks() {
        var clickedLinks = JSON.parse(localStorage.getItem('clickedLinks')) || {};
        var currentDate = new Date();

        if (Array.isArray(clickedLinks)) {
            clickedLinks = clickedLinks.reduce(function(obj, link) {
                obj[link] = {
                    expirationDate: new Date().toISOString()
                };
                return obj;
            }, {});
            localStorage.setItem('clickedLinks', JSON.stringify(clickedLinks));
        }

        Object.keys(clickedLinks).forEach(function(link) {
            if (new Date(clickedLinks[link].expirationDate) < currentDate) {
                delete clickedLinks[link];
            }
        });

        localStorage.setItem('clickedLinks', JSON.stringify(clickedLinks));
        return clickedLinks;
    }

    function addClickedClass(link) {
        if (!link.startsWith('http')) {
            return;
        }
        if (clickedLinks.hasOwnProperty(link)) {
            $(this).addClass('clicked');
        }
    }

    function handleLinkClick(event) {
        event.preventDefault();
        var link = $(this).attr('href');
        if (!clickedLinks.hasOwnProperty(link)) {
            var expirationDate = new Date();
            expirationDate.setMonth(expirationDate.getMonth() + 3);

            clickedLinks[link] = {
                expirationDate: expirationDate.toISOString()
            };

            localStorage.setItem('clickedLinks', JSON.stringify(clickedLinks));
        }
        $(this).addClass('clicked');
        window.open(link, '_blank');
    }

    function handleListGroupItemScroll(e) {
        e.preventDefault();
        var targetId = $(this).data('target');
        if (targetId) {
            var targetPosition = $(targetId).offset().top;
            $('html, body').animate({
                scrollTop: targetPosition
            }, 500);
        }
    }

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

    

    var clickedLinks = getClickedLinks();

    $('.hide-checkbox').on('mousedown', handleCheckboxClick);
    hideForm.submit(handleHideFormSubmit);
    initDatePicker();
    $('a').each(function() {
        var link = $(this).attr('href');
        addClickedClass.call(this, link);
    });
    $('a:not(.card-title a)').each(function() {
        var link = $(this).attr('href');
        addClickedClass.call(this, link);
    });
    $('a:not(.list-group-item, .card-title a, .date-navigation a, .navbar-nav a)').click(handleLinkClick);
    $('.list-group-item').click(handleListGroupItemScroll);

    $(document).ready(function() {
        $('.toggle-favorite').click(toggleFavorite);
    });

    $('.save-comment').on('click', function() {
        var articleId = $(this).data('article-id');
        var content = $(this).closest('.comment-form').find('.comment-textarea').val();
        saveComment(articleId, content);
        hideCommentSection(articleId);
    });

    $(document).on('click', '.delete-comment', function() {
        var articleId = $(this).data('article-id');
        if (confirm('このコメントを削除してもよろしいですか？')) {
            deleteComment(articleId);
        }
    });
    
    $(document).on('click', '.comment-icon', function(e) {
        e.stopPropagation();
        toggleCommentSection($(this));
    });
});