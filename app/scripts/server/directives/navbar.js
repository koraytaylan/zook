/*jslint browser: true*/
/*global app*/
'use strict';

app.directive('navbar', [ '$location', function ($location) {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/server/navbar.html',
        controller: function ($scope, $location) {
            $scope.isActive = function (viewLocation) {
                return viewLocation === $location.path();
            };
            console.log($location.path());
        }
    };
}]);