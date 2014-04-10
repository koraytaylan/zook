/*jslint browser: true*/
/*global app*/
'use strict';

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {templateUrl: 'home.html', controller: HomeCtrl})
        .when('/clients', {templateUrl: 'views/server/clients.html', controller: 'ClientsCtrl'})
        .when('/list', {templateUrl: 'list.html',   controller: ListCtrl})
        .when('/detail/:itemId', {templateUrl: 'detail.html',   controller: DetailCtrl})
        .when('/settings', {templateUrl: 'settings.html',   controller: SettingsCtrl})
        .otherwise({redirectTo: '/'});
}]);