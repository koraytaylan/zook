/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.directive('messageBox', [ function () {
    return {
        restrict: 'E',
        //transclude: true,
        scope: {},
        templateUrl: 'partials/message-box.html',
        controller: function ($scope) {
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
            }

            $scope.$on('message-box-open', function (event, message) {
                console.log(message);
                $scope.isActive = true;
                $scope.mode = message.mode || 'info';
                $scope.title = message.title || 'Message';
                $scope.content = message.content;
                $scope.isModal = message.modal || message.isModal;
            });

            $scope.$on('message-box-close', function () {
                $scope.close();
            });
        }
    };
}]);