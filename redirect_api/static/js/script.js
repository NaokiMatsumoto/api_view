$(document).ready(function() {
    var hideButton = $('#hideButton');
    var checkboxes = $('input[type="checkbox"]');
    var hideForm = $('#hideForm');

    function updateHideButtonVisibility() {
        var checkedCount = checkboxes.filter(':checked').length;
        hideButton.toggleClass('show', checkedCount > 0);
    }

    $(document).on('mousedown', '.list-group-item', function(e) {
        // チェックボックスまたはそのラベルがクリックされた場合は、デフォルトの動作を許可する
        if ($(e.target).is('a')) {
            return; // この場合は、以下のロジックを実行せずに早期に関数から抜ける
        }
        
        // アンカータグがクリックされた場合は、デフォルトの振る舞いを阻害しない
        e.preventDefault(); // これにより、アンカー以外の要素がクリックされた場合にのみデフォルト動作を阻害する
        var checkbox = $(this).find('.hide-checkbox');
        if(checkbox.is(':checked')){
            checkbox.prop('checked', false).attr('value', 'false'); // チェックボックスの状態を切り替える
        }else{
            checkbox.prop('checked', true).attr('value', 'true'); // チェックボックスの状態を切り替える
        }
        // ここでupdateHideButtonVisibilityを呼び出す
        updateHideButtonVisibility();
    });
    


    hideForm.submit(function(event) {
        event.preventDefault();
        var selectedArticleIds = [];
        checkboxes.filter(':checked').each(function() {
            selectedArticleIds.push($(this).data('article-id'));
        });

        $('<input>').attr({
            type: 'hidden',
            name: 'article_ids',
            value: selectedArticleIds.join(',')
        }).appendTo(hideForm);

        hideForm.off('submit').submit();
    });

    $('#datePicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true
    }).on('changeDate', function(e) {
        var selectedDate = e.format();
        var dateArray = selectedDate.split('-');
        var year = dateArray[0];
        var month = dateArray[1];
        var day = dateArray[2];
        window.location.href = `/news/${year}/${month}/${day}/`;
    });

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

    function addClickedClass(link) {
        if(!link.startsWith('http')){
            return;
        }
        if (clickedLinks.hasOwnProperty(link)) {
            $(this).addClass('clicked');
        }
    }

    $('a').each(function() {
        var link = $(this).attr('href');
        addClickedClass.call(this, link);
    });

    $('a:not(.card-title a)').each(function() {
        var link = $(this).attr('href');
        addClickedClass.call(this, link);
    });

    $('a:not(.list-group-item, .card-title a, .date-navigation a)').click(function(event) {
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
    });

    $('.list-group-item').click(function(e) {
        e.preventDefault();
        var targetId = $(this).data('target');
        if (targetId) {
            var targetPosition = $(targetId).offset().top;
            $('html, body').animate({
                scrollTop: targetPosition
            }, 500);
        }
    });

});