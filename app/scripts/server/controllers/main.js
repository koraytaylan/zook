/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isAuthorized = false;
    $scope.isStarted = false;
    $scope.isPaused = false;

    $scope.$on('socket-initialize', function (event, message) {
        var data = message.data;
        $scope.key = data.key;
        $scope.session = data.session;
        $scope.isAuthorized = data.is_experimenter;
    });

    $scope.authorize = function () {
        socket
            .send('authorize', {login: $scope.txtLogin, password: $scope.txtPassword})
            .then(function (message) {
                if (message.type !== 'invalid_operation') {
                    $scope.isAuthorized = true;
                    $scope.$broadcast('authorize');
                }
            });
    };
}]);