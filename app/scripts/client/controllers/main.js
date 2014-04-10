/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isStarted = false;
    $scope.isPaused = false;

    $scope.$on('state-waiting', function () {
        $scope.state = -1;
        $scope.isWaiting = true;
    });

    $scope.$on('state-initial', function () {
        $scope.state = 0;
        $scope.isWaiting = false;
    });

    socket.onInitialize(function (message) {
        var data = message.data;
        $scope.key = data.key;
        $scope.session = data.session;
    });
}]);