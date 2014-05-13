/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.directive('connection', [ 'SocketService', function (socket) {
    return {
        restrict: 'E',
        scope: {},
        templateUrl: 'partials/connection.html',
        controller: 'ConnectionCtrl'
    };
}]);