/*jslint browser: true*/
/*global app*/
'use strict';

app.directive('navbar', [ function () {
    return {
        restrict: 'E',
        transclude: true,
        scope: {},
        templateUrl: 'partials/server/navbar.html'
    };
}]);