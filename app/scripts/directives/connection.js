/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.directive('connection', [ 'SocketService', function (socket) {
    return {
        restrict: 'E',
        //transclude: true,
        scope: {},
        templateUrl: 'partials/connection.html',
        controller: function ($scope) {
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

            $scope.$on('socket-close', function () {
                $scope.isConnected = false;
                $scope.status = 'Connection dropped. Please try to reconnect.';
                $scope.$apply();
            });

            $scope.$on('socket-initialize', function () {
                $scope.isConnecting = socket.isInitializing;
                $scope.isConnected = socket.isInitialized;
            });
        }
    };
}]);