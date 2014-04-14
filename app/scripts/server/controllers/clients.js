/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('ClientsCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isInitialized = false;
    $scope.isLoading = true;
    $scope.subjects = [];

    $scope.setError = function (errorMessage) {
        $scope.showError = true;
        $scope.errorMessage = errorMessage;
    };

    $scope.getSubjects = function () {
        $scope.isLoading = true;
        socket.send('get_subjects').then(function (message) {
            $scope.isLoading = false;
            $scope.subjects = message.data;
        });
        $scope.isInitialized = true;
    };

    $scope.remove = function (key) {
        $scope.isLoading = true;
        socket.send('delete_subject', key).then(function (message) {
            $scope.isLoading = false;
            if (message.type === 'invalid_operation') {
                $scope.setError(message.data);
            } else {
                var s = null;
                for (var i = 0; i < $scope.subjects.length; i++) {
                    var ss = $scope.subjects[i];
                    if (ss.key == key) {
                        s = ss;
                        break;
                    }
                };
                if (s !== null) {
                    var i = $scope.subjects.indexOf(s);
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
}]);