// @todo move into static asset 

function todo() {
    alert('Todo!');
    return false;
}

// Saved searched
function saveSearch() {
    var modal = new bootstrap.Modal(document.getElementById('savedSearchModal'))
    if (!USER) {
        alert('Please login or register');
        return;
    }
    const params = new URLSearchParams(location.search);

    $.ajax({
        url: '/api/saved-search/add',
        type: 'post',
        data: {
            'animal_type': params.get('animal_type'),
            'zip': params.get('zip'),
            'radius': params.get('radius') || 50,
            'age': params.get('age'),
            'size': params.get('size'),
            'sex': params.get('sex'),
            'breed': params.get('breed'),
            'euth_date_within_days': params.get('euth_date'),
            'goodwith_cats': params.has('goodwith_cats') || null,
            'goodwith_dogs': params.has('goodwith_dogs') || null,
            'goodwith_kids': params.has('goodwith_kids') || null,
        },
        headers: csrfHeaders(),
    }).then(function (result) {
        $('#savedSearchModalSearchName').html(result.name);
        modal.show();
    });
}

// Localize timestamp spans
$('[data-timestamp]').each(function (idx, el) {
    el = $(el);
    var dte = new Date(el.data('timestamp'));
    var fmt = new Intl.DateTimeFormat([], { dateStyle: 'full', timeStyle: 'long' });
    el.text(fmt.format(dte));
});

$(document).ready(function () {
    // click event on the reply buttons
    $('.reply').click(function (button) {
        let buttonID = button.target.id;

        // Reply form element
        var replyForm = `
        <form method="post" id="reply-form${buttonID}" class="reply-form" onsubmit="submitForm(event)">
            <input type="hidden" name="comment_id" value="${buttonID}">
                <textarea rows="3" name="body" required></textarea>
                <input type="submit" class="btn btn-primary reply-button" value="Add your reply">
        </form>`;

        // display/append the form under the exact comment
        var formInstance = document.getElementById('reply-form' + buttonID)
        if (!formInstance) {
            $('#comment-' + buttonID + ' .sub-comments').append(replyForm);
        }
    });
});

function submitForm(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const formProps = Object.fromEntries(formData);
    var commentID = formProps.comment_id;
    var formBody = formProps.body;
    $.ajax({
        url: `/comments/${commentID}/reply`,
        type: 'post',
        data: {
            'body': formBody,
            'comment_id': commentID
        },
        headers: csrfHeaders(),
        success: function (response) {
            window.location.reload();
        },
    });
}

function csrfHeaders() {
    return {
        'X-CSRFToken': document.getElementById('csrf').querySelector('input').value
    };
}

function toggleShortlistSmall(el, animalId) {
    if (!USER) {
        alert('Please login or register');
        return;
    }
    var wasSet = $(el).hasClass('animal-shortlist-selected');
    $(el).toggleClass('animal-shortlist-selected');
    var isSet = !wasSet;
    if (isSet) {
        $(el).html('<i class="bi-heart-fill"></i>');
    } else {
        $(el).html('<i class="bi-heart"></i>');
    }
    setShortlist(animalId, isSet);
}

function toggleShortlistLarge(el, animalId) {
    if (!USER) {
        alert('Please login or register');
        return;
    }
    var wasSet = $(el).hasClass('btn-primary');
    $(el).toggleClass('btn-primary').toggleClass('btn-secondary');
    var isSet = !wasSet;
    if (isSet) {
        $(el).html('<i class="bi-heart-fill"></i> Favorited');
    } else {
        $(el).html('<i class="bi-heart"></i> Add to favorites');
    }
    setShortlist(animalId, isSet);
}

function setShortlist(animalId, isSet) {
    $.ajax({
        url: '/api/shortlist',
        type: 'post',
        data: {
            'animalId': animalId,
            'isSet': isSet,
        },
        headers: csrfHeaders(),
    });
}