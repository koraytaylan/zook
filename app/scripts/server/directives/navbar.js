/*jslint browser: true*/
/*global app*/
'use strict';

app.directive('navbar', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/server/navbar.html',
        controller: 'MainCtrl'
    };
}]);