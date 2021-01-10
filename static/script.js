// Search for anime titles function (Source: Week 9 lecture)
function titleSearch(input_id) {
    let input = document.querySelector(input_id);

    input.addEventListener('keyup', function() {
        $.get('/title-search?q=' + input.value, function(anime) {
            let html = '';
            for (let id in anime)
            {
                let title = anime[id].title;
                let titleEn = anime[id].title_english;
                if (titleEn.localeCompare("") != 0 && titleEn.localeCompare(title) != 0)
                {
                    html += '<option value="' + title + ' (English: ' + titleEn + ')">';
                }
                else
                {
                    html += '<option value="' + title + '">';
                }
            }
            document.querySelector('#lists').innerHTML = html;
        });
    });
}

// Search for users function (Source: Week 9 lecture)
function userSearch(input_id) {
    let input = document.querySelector(input_id);

    input.addEventListener('keyup', function() {
        $.get('/user-search?q=' + input.value, function(users) {
            let html = '';
            for (let id in users)
            {
                let username = users[id].username;

                html += '<option value="' + username + '">';
            }
            document.querySelector('#lists').innerHTML = html;
        });
    });
}

// Select multiple users
function selectMultiple() {
    $(document).ready(function(){

         var multipleCancelButton = new Choices('#choices-multiple-remove-button', {
         removeItemButton: true,
         maxItemCount:10,
         searchResultLimit:10,
         renderChoiceLimit:10
         });
     });
}