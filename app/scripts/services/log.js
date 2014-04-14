/*jslint browser: true*/
/*global angular, app, WebSocket, localStorage*/
'use strict';

app.factory('LogService', [function () {
    var service = {},
        log = function (color, message, data) {
            var args = [
                '%c >',
                'background:' + color + '; color: white;',
                message
            ];
            if (data && data !== null) {
                args.push(data);
            }
            //console.log('%c>>>', 'background:' + color + '; color: white;', message, data);
            try {
                console.log.apply(console, args);
            } catch (ignore) {}
        };

    service.info = function (message, data) {
        log('blue', message, data);
    };

    service.success = function (message, data) {
        log('green', message, data);
    };

    service.error = function (message, data) {
        log('red', message, data);
    };

    service.info = function (message, data) {
        log('blue', message, data);
    };

    service.warning = function (message, data) {
        log('orange', message, data);
    };

    return service;
}]);