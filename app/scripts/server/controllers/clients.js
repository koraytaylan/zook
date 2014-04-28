/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('ClientsCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isLoading = true;
    $scope.subjects = [];

    $scope.predicate = 'name';
    $scope.reverse = false;

    $scope.Math = window.Math;
/*
    socket.onMessage(function (message) {
        if (message.type === 'set_subject'
                || message.type === 'initialize') {
            $scope.getSubjects();
        }
    });
*/

    $scope.setError = function (errorMessage) {
        $scope.showError = true;
        $scope.errorMessage = errorMessage;
    };

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
        socket.send('suspend_subject', key).then(function (message) {
            $scope.isLoading = false;
            if (message.isError) {
                $scope.setError(message.data);
            } else {
                $scope.getSubjects();
            }
        });
    };

    $scope.$on('authorized', function () {
        $scope.getSubjects();
    });

    if (socket.isInitialized) {
        $scope.getSubjects();
    }
/*
    socket.onInitialize(function () {
        $scope.getSubjects();
    });
*/
    $scope.$on('socket-initialized', function () {
        $scope.getSubjects();
    });

    $scope.$on('socket-receive', function (event, message) {
        if (message.type === 'set_subject'
                || message.type === 'get_subject') {
            $scope.getSubjects();
        }
    });
}]);