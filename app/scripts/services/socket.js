/*jslint browser: true*/
/*global angular, app, WebSocket, localStorage*/
'use strict';

app.factory('SocketService', ['$q', '$rootScope', 'LogService', function ($q, $rootScope, log) {
    var socket = {},
        callbacks = {},
        lastId = 0,
        ws = null;

    socket.isOpen = false;
    socket.isInitializing = true;
    socket.isInitialized = false;

    socket.send = function (type, message) {
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

    socket.initialize = function () {
        var defer = $q.defer();
        ws = new WebSocket("ws://localhost:8080/socket");
        socket.isInitializing = true;
        ws.onopen = function () {
            socket.isOpen = true;
            log.info("Socket: opened!");
            socket
                .send('initialize', localStorage.getItem('socket.key'))
                .then(
                    function (message) {
                        socket.isInitializing = false;
                        var data = message.data;
                        localStorage.setItem('socket.key', data.key);
                        socket.isInitialized = true;
                        log.info("Socket: initialized");
                        defer.resolve(message);
                        $rootScope.$broadcast('socket-initialized', message);
                    },
                    function (message) {
                        socket.isInitializing = false;
                        ws.close();
                        defer.reject(message);
                    }
                );
        };

        ws.onclose = function () {
            socket.isInitialized = false;
            socket.isOpen = false;
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
                        $rootScope.$apply(cb.defer.resolve(message));
                    } else {
                        message.isError = true;
                        log.error(logMessage, message);
                        $rootScope.$apply(cb.defer.reject(message));
                    }
                    delete callbacks[message.id];
                } else {
                    message.isReply = false;
                    log.info('Socket: message received', message);
                }
                $rootScope.$broadcast('socket-received', message);
            }
        };

        return defer.promise;
    };

    socket.close = function () {
        ws.close();
    };

    socket.initialize().then(function (message) {
        
    });

    window.socket = socket;

    return socket;
}]);