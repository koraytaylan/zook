/*jslint browser: true*/
/*global angular, app, $*/
'use strict';

app.controller('MainCtrl', [ '$scope', '$location', 'SocketService', function ($scope, $location, socket) {
    $scope.isAuthorized = false;
    $scope.session = {};

    $scope.$on('socket-initialized', function (event, message) {
        var data = message.data;
        $scope.key = data.key;
        $scope.session = $.extend($scope.session, data.session);
        $scope.isAuthorized = data.is_experimenter;
    });

    $scope.isActiveLocation = function (viewLocation) {
        return viewLocation === $location.path();
    };

    $scope.authorize = function () {
        socket
            .send('authorize', {login: $scope.txtLogin, password: $scope.txtPassword})
            .then(
                function () {
                    $scope.isAuthorized = true;
                    $scope.$broadcast('authorized');
                },
                function (message) {
                    $scope.$broadcast('message-box-open', {
                        modal: true,
                        mode: 'error',
                        content: message.data
                    });
                }
            );
    };

    var sessionAction = function (action) {
        socket
            .send(action)
            .then(
                function (message) {
                    $scope.session = $.extend($scope.session, message.data);
                },
                function (message) {
                    $scope.$broadcast('message-box-open', {
                        modal: true,
                        mode: 'error',
                        content: message.data
                    });
                }
            );
    };

    $scope.start = function () {
        sessionAction('start_session');
    };

    $scope.pause = function () {
        sessionAction('pause_session');
    };

    $scope.resume = function () {
        sessionAction('resume_session');
    };

    $scope.stop = function () {
        sessionAction('stop_session');
    };

    $scope.skipPhase = function () {
        sessionAction('skip_phase');
    };

    $scope.$on('socket-received', function (event, message) {
        if (message.type === 'get_session') {
            $scope.session = $.extend($scope.session, message.data);
        }
        $scope.$apply();
    });
}]);