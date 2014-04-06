/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('SubjectController', [ '$scope', 'socket', function ($scope, socket) {
    $scope.getYourName = function () {
        return $scope.yourName;
    };

    $scope.sendMessage = function () {
        socket.echo($scope.txtYourName).then(function (message) {
            $scope.yourName = message.data;
        });
    };

    socket.onInitialize(function () {
        socket.send('echo');
    });
}]);