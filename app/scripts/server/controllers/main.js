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
            .then(function () {
                $scope.isAuthorized = true;
                $scope.$broadcast('authorized');
            });
    };

    $scope.start = function () {
        socket
            .send('start_session')
            .then(function (message) {
                $scope.session = $.extend($scope.session, message.data);
                console.dir($scope.session);
            });
    };

    $scope.stop = function () {
        socket
            .send('stop_session')
            .then(function (message) {
                $scope.session = $.extend($scope.session, message.data);
            });
    };

    $scope.skipPhase = function () {
        socket
            .send('skip_phase');
    };
}]);