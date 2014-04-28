/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.directive('subjectInitialize', [ 'SocketService', function (socket) {
    return {
        restrict: 'E',
        //transclude: true,
        scope: {},
        templateUrl: 'partials/client/subject-initialize.html',
        controller: function ($scope) {

            $scope.$on('continue', function () {
                var name = $scope.txtClientName || 'Client1';
                socket.send('set_subject', {
                    status: 'waiting',
                    name: name
                }).then(function (message) {
                    if (message.type === 'invalid_operation') {
                        $scope.errorMessage = message.data;
                        $scope.showError = true;
                        $scope.$emit('state-initial');
                    } else {
                        $scope.$emit('state-waiting');
                    }
                });
            });
        }
    };
}]);