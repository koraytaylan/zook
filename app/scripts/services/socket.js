/*jslint browser: true*/
/*global angular, app, WebSocket, localStorage*/
'use strict';

app.factory('SocketService', ['$q', '$rootScope', 'LogService', function ($q, $rootScope, log) {
    var service = {},
        callbacks = {},
        lastId = 0,
        ws = null;

    service.isOpen = false;
    service.isInitializing = true;
    service.isInitialized = false;

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
        var defer = $q.defer();
        ws = new WebSocket("ws://localhost:8080/socket");
        service.isInitializing = true;
        ws.onopen = function () {
            service.isOpen = true;
            log.info("Socket: opened!");
            service.send('initialize', localStorage.getItem('key')).then(function (message) {
                service.isInitializing = false;
                if (!message.isError) {
                    var data = message.data;
                    localStorage.setItem('key', data.key);
                    service.isInitialized = true;
                    defer.resolve(message);
                    log.info("Socket: initialized");
                    $rootScope.$broadcast('socket-initialized', message);
                } else {
                    ws.close();
                    defer.reject(message);
                }
            });
        };

        ws.onclose = function () {
            service.isInitialized = false;
            service.isOpen = false;
            log.info("Socket: closed!");
            $rootScope.$broadcast('socket-closed');
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
                        message.isError = true;
                        log.error(logMessage, message);
                    }
                    $rootScope.$apply(cb.defer.resolve(message));
                    delete callbacks[message.id];
                } else {
                    message.isReply = false;
                    log.info('Socket: message received', message);
                    $rootScope.$broadcast('socket-receive', message);
                }
            }
        };

        return defer.promise;
    };

    service.close = function () {
        ws.close();
    };

    service.initialize();

    window.socket = service;

    return service;
}]);