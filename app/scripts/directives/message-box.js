/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.directive('messageBox', [ function () {
    return {
        restrict: 'E',
        scope: {},
        templateUrl: 'partials/message-box.html',
        controller: 'MessageBoxCtrl'
    };
}]);