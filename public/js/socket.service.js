/*jslint browser: true*/
/*global angular, app, WebSocket, localStorage*/
app.factory('SocketService', ['$q', '$rootScope', function ($q, $rootScope) {
    'use strict';
    var service = {},
        callbacks = {},
        lastId = 0,
        onOpenCallbacks = [],
        onCloseCallbacks = [],
        onInitializeCallbacks = [],
        ws = null,
        notify = function () {
            var args = arguments,
                cbs = [].shift.apply(args);
            angular.forEach(cbs, function (callback) {
                callback.apply(this, args);
            });
        };

    ws = new WebSocket("ws://localhost:8080/socket");

    service.isInitialized = false;

    service.onOpen = function (callback) {
        onOpenCallbacks.push(callback);
    };

    service.onClose = function (callback) {
        onCloseCallbacks.push(callback);
    };

    service.onInitialize = function (callback) {
        onInitializeCallbacks.push(callback);
    };

    service.send = function (type, message) {
        lastId += 1;
        var defer = $q.defer(),
            request = {
                id: lastId,
                timestamp: new Date().getTime(),
                type: type,
                data: message
            };
        callbacks[request.id] = {
            timestamp: request.timestamp,
            defer: defer
        };
        console.log('Socket: sending message', request);
        ws.send(JSON.stringify(request));
        return defer.promise;
    };

    service.initialize = function () {
        return service.send('initialize', localStorage.getItem('key')).then(function (message) {
            var data = message.data;
            localStorage.setItem('key', data.key);
            service.isInitialized = true;
            return message;
        });
    };

    service.echo = function (message) {
        return service.send('echo', message);
    };

    ws.onopen = function () {
        console.log("Socket: opened!");
        notify(onOpenCallbacks);
        service.initialize().then(function (message) {
            notify(onInitializeCallbacks, message);
        });
    };

    ws.onclose = function () {
        console.log("Socket: closed!");
        notify(onCloseCallbacks);
    };

    ws.onmessage = function (message) {
        var cb = null;
        try {
            message = JSON.parse(message.data);
        } catch (ex) {
            console.log('Socket: invalid message received', message);
        }
        if (message !== null) {
            if (callbacks.hasOwnProperty(message.id)) {
                cb = callbacks[message.id];
                message.isReply = true;
                message.roundtrip = new Date().getTime() - cb.timestamp;
                console.log('Socket: message reply received ' + message.roundtrip + 'ms', message);
                $rootScope.$apply(cb.defer.resolve(message));
                delete callbacks[message.id];
            } else {
                message.isReply = false;
                console.log('Socket: message received', message);
            }
        }
    };

    return service;
}]);