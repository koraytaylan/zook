/*jslint browser: true*/
/*global angular*/
'use strict';

var app = angular.module('zook', ['ngRoute']);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/clients', {templateUrl: 'views/server/clients.html', controller: 'ClientsCtrl'})
        .when('/settings', {templateUrl: 'views/server/clients.html',   controller: 'ClientsCtrl'})
        .otherwise({redirectTo: '/clients'});
}]);