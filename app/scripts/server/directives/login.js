/*jslint browser: true*/
/*global app*/
'use strict';

app.directive('login', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/server/login.html',
        controller: function () {
        }
    };
}]);