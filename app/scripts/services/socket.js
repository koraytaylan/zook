/*jslint browser: true*/
/*global angular, app, WebSocket, localStorage*/
'use strict';

app.factory('SocketService', ['$q', '$rootScope', 'LogService', function ($q, $rootScope, log) {
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
            defer: defer,
            type: type
        };
        log.info('Socket: sending message', request);
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

    service.close = function () {
        ws.close();
    };

    ws.onopen = function () {
        log.info("Socket: opened!");
        notify(onOpenCallbacks);
        service.initialize().then(function (message) {
            notify(onInitializeCallbacks, message);
        });
    };

    ws.onclose = function () {
        log.info("Socket: closed!");
        notify(onCloseCallbacks);
    };

    ws.onmessage = function (message) {
        var cb = null,
            logMessage = null;
        try {
            message = JSON.parse(message.data);
        } catch (ex) {
            log.error('Socket: invalid message received', message);
        }
        if (message !== null) {
            if (callbacks.hasOwnProperty(message.id)) {
                cb = callbacks[message.id];
                message.isReply = true;
                message.roundtrip = new Date().getTime() - cb.timestamp;
                logMessage = 'Socket: message reply received ' + message.roundtrip + 'ms';
                if (cb.type === message.type) {
                    log.success(logMessage, message);
                } else {
                    log.error(logMessage, message);
                }
                $rootScope.$apply(cb.defer.resolve(message));
                delete callbacks[message.id];
            } else {
                message.isReply = false;
                log.info('Socket: message received', message);
            }
        }
    };

    window.socket = service;

    return service;
}]);