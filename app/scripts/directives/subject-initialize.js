/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.directive('subjectInitialize', [ 'SocketService', function (socket) {
    return {
        restrict: 'E',
        //transclude: true,
        scope: {},
        templateUrl: 'partials/subject-initialize.html',
        controller: function ($scope) {

            $scope.$on('continue', function () {
                socket.send('set_subject', {
                    name: $scope.txtClientName
                }).then(function (message) {
                    if (message.type === 'invalid_operation') {
                        $scope.errorMessage = message.data;
                        $scope.showError = true;
                    } else {
                        $scope.$emit('wait');
                    }
                });
            });
        }
    };
}]);