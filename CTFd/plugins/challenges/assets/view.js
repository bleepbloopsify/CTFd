window.challenge.data = undefined;

window.challenge.renderer = new markdownit({
    html: true,
});

window.challenge.preRender = function () {

};

window.challenge.render = function (markdown) {
    return window.challenge.renderer.render(markdown);
};


window.challenge.postRender = function () {

};


window.challenge.submit = function (cb, preview) {
    var challenge_id = parseInt($('#chal-id').val());
    var submission = $('#answer-input').val();

    var url = "/api/v1/challenges/attempt";
    // if (preview) {
    //     url = "/admin/chal/";
    // }

    var params = {
        'challenge_id': challenge_id,
        'submission': submission
    };

    fetch(script_root + url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in.
            window.location = script_root + "/login?next=" + script_root + window.location.pathname + window.location.hash;
        }
        return response.json();
    }).then(function (response) {
        cb(response);
    });
};