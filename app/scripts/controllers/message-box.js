/*jslint browser: true*/
/*global angular, app, $*/
'use strict';

app.controller('MessageBoxCtrl', [ '$scope', '$rootScope', function ($scope, $rootScope) {
    var initialize = function () {
        $scope.isActive = false;
        $scope.isModal = false;
        $scope.mode = 'info';
        $scope.title = 'Title';
        $scope.content = 'Content';
    };

    initialize();

    $scope.close = function () {
        initialize();
    };

    $scope.$on('message-box-open', function (event, message) {
        $scope.isActive = true;
        $scope.mode = message.mode || 'info';
        $scope.title = message.title || (message.mode == 'error' && 'Error') || 'Message';
        $scope.content = message.content;
        $scope.isModal = message.modal || message.isModal;
    });

    $scope.$on('message-box-close', function () {
        $scope.close();
    });
}]);