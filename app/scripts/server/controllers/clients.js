/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('ClientsCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isInitialized = false;
    $scope.isLoading = true;
    $scope.subjects = [];

    $scope.getSubjects = function () {
        $scope.isLoading = true;
        socket.send('get_subjects').then(function (message) {
            $scope.isLoading = false;
            $scope.subjects = message.data;
        });
        $scope.isInitialized = true;
    };

    socket.onInitialize(function (message) {
        if (!$scope.isInitialized) {
            $scope.getSubjects();
        }
    });

    if ($scope.isInitialized) {
        $scope.getSubjects();
    }
}]);