/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('ClientsCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isLoading = true;
    $scope.subjects = [];

    $scope.predicate = 'name';
    $scope.reverse = false;

    $scope.Math = window.Math;

    $scope.suspend = function (key) {
        $scope.isLoading = true;
        socket.send('suspend_subject', key).then(function () {
            $scope.isLoading = false;
            socket.send('get_session');
        });
    };

    $scope.$on('socket-received', function (event, message) {
        if (message.type === 'set_session'
                || message.type === 'get_session') {
            $scope.session = message.data;
        }
        $scope.$apply();
    });
}]);