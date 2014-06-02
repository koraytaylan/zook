/*jslint browser: true*/
/*global angular*/
'use strict';

var app = angular.module('zook', ['ngRoute']);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/clients', {templateUrl: 'partials/server/clients.html', controller: 'ClientsCtrl'})
        .when('/settings', {templateUrl: 'partials/server/settings.html', controller: 'SettingsCtrl'})
        .otherwise({redirectTo: '/clients'});
}]);

app.filter('currency', ['$filter', function ($filter) {
    return function (amount) {
        var isNegative = amount < 0;
        if (isNegative) {
            amount = -1 * amount;
        }
        return (isNegative ? '-$' : '$')
            + $filter('number')(amount, 2);
    };
}]);