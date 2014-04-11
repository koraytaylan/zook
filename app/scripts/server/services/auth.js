/*jslint browser: true*/
/*global angular, app, WebSocket, localStorage*/
'use strict';

app.factory('AuthService', ['$rootScope', 'SocketService', function ($rootScope, socket) {
    var service = {};
    service.isAuthorized = false;

    return service;
}]);