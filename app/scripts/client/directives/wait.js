/*jslint browser: true*/
/*global app*/
'use strict';

app.directive('wait', [ function () {
    return {
        restrict: 'E',
        transclude: true,
        scope: {},
        templateUrl: 'partials/client/wait.html'
    };
}]);