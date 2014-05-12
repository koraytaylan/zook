/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('ClientsCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isLoading = true;
    $scope.subjects = [];

    $scope.predicate = 'name';
    $scope.reverse = false;

    $scope.Math = window.Math;

    $scope.getSubjects = function () {
        $scope.isLoading = true;
        socket.send('get_subjects').then(function (message) {
            $scope.isLoading = false;
            if (!message.isError) {
                $scope.subjects = message.data;
            }
        });
    };

    $scope.suspend = function (key) {
        $scope.isLoading = true;
        socket.send('suspend_subject', key).then(function () {
            $scope.isLoading = false;
            $scope.getSubjects();
        });
    };
/*
    $scope.$on('authorized', function () {
        $scope.getSubjects();
    });

    if (socket.isInitialized) {
        $scope.getSubjects();
    }

    $scope.$on('socket-initialized', function () {
        $scope.getSubjects();
    });
*/

    $scope.$on('socket-received', function (event, message) {
        if (message.type === 'set_session'
                || message.type === 'get_session') {
            $scope.session = message.data;
        }
        $scope.$apply();
    });
}]);