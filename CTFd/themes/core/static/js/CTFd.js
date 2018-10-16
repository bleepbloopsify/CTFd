var CTFd = (function () {

    var urlRoot = '';

    const config = {
        get: () => fetch(`${urlRoot}/api/v1/configs`).then(r => r.json()),
        mode: {
            get: () => fetch(`${urlRoot}/api/v1/configs/user_mode`).then(r => r.json()),
        },
    };

    const me = {
        team: {
            info: {
                get: () => fetch(`${urlRoot}/api/v1/teams/me`).then(r => r.json()),
                /**
                 * data = { }
                 */
                patch: data => fetch(`${urlRoot}/api/v1/teams/me`, {
                    method: 'PATCH',
                    body: JSON.stringify(data),
                }).then(r => r.json()),
            },
            mail: {
                post: () => fetch(`${urlRoot}/api/v1/teams/me/mail`, {
                    method: 'POST', // TODO: fix when implemented
                }).then(r => r.json()),
            },
            solves: {
                get: () => fetch(`${urlRoot}/api/v1/teams/me/solves`).then(r => r.json()),
            },
            fails: {
                get: () => fetch(`${urlRoot}/api/v1/teams/me/fails`).then(r => r.json()),
            },
            awards: {
                get: () => fetch(`${urlRoot}/api/v1/teams/me/awards`).then(r => r.json()),
            },
        },
        user: {
            info: {
                get: () => fetch(`${urlRoot}/api/v1/users/me`).then(r => r.json()),
                /**
                 * data = { name, email, website, country, affiliation, bracket }
                 * NOTE: I'm not actually sure if affiliation is editable?
                 * the field looks slightly strange.
                 */
                patch: data => fetch(`${urlRoot}/api/v1/users/me`, {
                    method: 'PATCH',
                    body: JSON.stringify(data),
                }).then(r => r.json()),
            },
            mail: {
                /**
                 * there are no parameters here yet because the route is not 
                 * yet implemented
                 */
                post: () => fetch(`${urlRoot}/api/v1/users/me/mail`, {
                    method: 'POST', // TODO: fix when implemented
                }).then(r => r.json()),
            },
            solves: {
                get: () => fetch(`${urlRoot}/api/v1/users/me/solves`).then(r => r.json()),
            },
            fails: {
                get: () => fetch(`${urlRoot}/api/v1/users/me/fails`).then(r => r.json()),
            },
            awards: {
                get: () => fetch(`${urlRoot}/api/v1/users/me/awards`).then(r => r.json()),
            },
        },
    };

    const submissions = {
        post: data => {

        }
    };

    var challenges = {
        all: function(){
            return fetch(urlRoot + '/api/v1/challenges')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        get: function(challengeId){
            return fetch(urlRoot + '/api/v1/challenges/' + challengeId)
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    data.solves = function () {
                        return fetch(urlRoot + '/api/v1/challenges/' + this.id + '/solves')
                            .then(function (response) {
                                return response.json();
                            }).then(function (data) {
                                return data;
                            });
                    };

                    
                    return data;
                });
        },
        types: function(){
            return fetch(urlRoot + '/api/v1/challenges/types')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        solves: function () {
            return fetch(urlRoot + '/api/v1/statistics/challenges/solves')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        }
    };

    var scoreboard = function() {
        return fetch(urlRoot + '/api/v1/scoreboard')
            .then(function (response) {
                return response.json();
            }).then(function (data) {
                return data;
            });
    };

    var teams = {
        all: function () {
            return fetch(urlRoot + '/api/v1/teams')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        get: function (teamId) {
            return fetch(urlRoot + '/api/v1/teams/' + teamId)
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    data.solves = function () {

                    };
                    data.fails = function () {

                    };
                    data.awards = function () {

                    };
                    return data;
                });
        },
    };

    var users = {
        all: function () {
            return fetch(urlRoot + '/api/v1/users')
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    return data;
                });
        },
        get: function (userId) {
            return fetch(urlRoot + '/api/v1/users/' + userId)
                .then(function (response) {
                    return response.json();
                }).then(function (data) {
                    data.solves = function () {

                    };
                    data.fails = function () {

                    };
                    data.awards = function () {

                    };
                    return data;
                });
        },
    };

    return {
        me,
        config,
        challenges: challenges,
        scoreboard: scoreboard,
        teams: teams,
        users: users,
    };
})();