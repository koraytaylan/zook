app.factory('SocketService', ['$q', '$rootScope', function($q, $rootScope) {
    // We return this object to anything injecting our service
    var service = {};
    // Keep all pending requests here until they get responses
    var callbacks = {};
    // Create a unique callback ID to map requests to responses
    var currentId = 0;

    var notify = function () {
        var args = arguments;
        var callbacks = [].shift.apply(args);
        angular.forEach(callbacks, function(callback){
            callback.apply(this, args);
        });  
    };

    var onOpenCallbacks = [];
    service.onOpen = function (callback) {
        onOpenCallbacks.push(callback);
    };

    var onCloseCallbacks = [];
    service.onClose = function (callback) {
        onCloseCallbacks.push(callback);
    }

    var onInitializeCallbacks = [];
    service.onInitialize = function (callback) {
        onInitializeCallbacks.push(callback);
    }

    // Create our websocket object with the address to the websocket
    var ws = new WebSocket("ws://localhost:8080/socket");

    service.isInitialized = false;
    service.send = function (type, message) {
        var defer = $q.defer();
        var request = {
            id: ++currentId,
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
            localStorage.setItem('key', message.data);
            service.isInitialized = true;
        });
    };

    service.echo = function (message) {
        return service.send('echo', message);
    };

    ws.onopen = function(){  
        console.log("Socket: opened!");
        notify(onOpenCallbacks);
        service.initialize().then(function() {
            notify(onInitializeCallbacks);
        });
    };

    ws.onclose = function () {
        console.log("Socket: closed!");
        notify(onCloseCallbacks);
    };

    ws.onmessage = function(message) {
        var data = JSON.parse(message.data);
        data.roundtrip = new Date().getTime() - data.timestamp;
        console.log('Socket: message received ' + data.roundtrip + 'ms', data);
        if(callbacks.hasOwnProperty(data.id)) {
            var cb = callbacks[data.id];
            $rootScope.$apply(cb.defer.resolve(data));
            delete callbacks[data.id];
        }
    };

    return service;
}]);