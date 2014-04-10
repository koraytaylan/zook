/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isAuthorized = false;
    $scope.isStarted = false;
    $scope.isPaused = false;

    socket.onInitialize(function (message) {
        var data = message.data;
        $scope.key = data.key;
        $scope.session = data.session;
    });
}]);