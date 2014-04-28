/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('ClientsCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isLoading = true;
    $scope.subjects = [];

    $scope.predicate = 'name';
    $scope.reverse = false;
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

    $scope.remove = function (key) {
        $scope.isLoading = true;
        socket.send('delete_subject', key).then(function (message) {
            var i = 0,
                s = null,
                ss = null;
            $scope.isLoading = false;
            if (message.type === 'invalid_operation') {
                $scope.setError(message.data);
            } else {
                for (i = 0; i < $scope.subjects.length; i += 1) {
                    ss = $scope.subjects[i];
                    if (ss.key === key) {
                        s = ss;
                        break;
                    }
                }
                if (s !== null) {
                    i = $scope.subjects.indexOf(s);
                    $scope.subjects.splice(i, 1);
                }
            }
        });
    };

    $scope.$on('authorize', function () {
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
    $scope.$on('socket-initialize', function () {
        $scope.getSubjects();
    });

    $scope.$on('socket-receive', function (event, message) {
        if (message.type === 'set_subject'
                || message.type === 'get_subject') {
            $scope.getSubjects();
        }
    });

    $scope.$on('$destroy', function () {
        console.log('Clients controller destroyed');
    });
}]);