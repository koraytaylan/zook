/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.directive('subjectInitialize', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/subject-initialize.html'
    };
}]);