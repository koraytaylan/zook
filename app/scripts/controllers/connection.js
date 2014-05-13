/*jslint browser: true*/
/*global angular, app, $*/
'use strict';

app.controller('ConnectionCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isConnecting = socket.isInitializing;
    $scope.isConnected = socket.isInitialized;

    $scope.reconnect = function () {
        if (!$scope.isConnected) {
            $scope.isConnecting = true;
            socket.initialize().then(function (message) {
                $scope.isConnecting = false;
                if (message.isError) {
                    $scope.isConnected = false;
                    $scope.status = message.data;
                } else {
                    $scope.isConnected = true;
                }
            });
        }
    };

    $scope.$on('socket-closed', function () {
        $scope.isConnecting = false;
        $scope.isConnected = false;
        $scope.status = 'Connection dropped. Please try to reconnect.';
        $scope.$apply();
    });

    $scope.$on('socket-initialized', function () {
        $scope.isConnecting = socket.isInitializing;
        $scope.isConnected = socket.isInitialized;
    });
}]);