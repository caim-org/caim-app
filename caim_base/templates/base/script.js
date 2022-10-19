// @todo move into static asset 

function todo() {
    alert('Todo!');
    return false;
}

// Saved searched
function saveSearch(){
    if (!USER) {
        alert('Please login or register');
        return;
    }
    const params = Object.fromEntries(new URLSearchParams(location.search));

    $.ajax({
        url: '/api/saved-search/add',
        type: 'post',
        data: {
            'search': params,
        },
        headers: csrfHeaders(),
    }).then(function(){
        alert('Saved');
    });
}

// Localize timestamp spans
$('[data-timestamp]').each(function (idx, el) {
    el = $(el);
    var dte = new Date(el.data('timestamp'));
    var fmt = new Intl.DateTimeFormat([], { dateStyle: 'full', timeStyle: 'long' });
    el.text(fmt.format(dte));
});

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
        $(el).html('<i class="bi-heart-fill"></i> Added to shortlist');
    } else {
        $(el).html('<i class="bi-heart"></i> Add to shortlist');
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