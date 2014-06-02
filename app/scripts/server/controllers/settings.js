/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('SettingsCtrl', [ '$scope', '$rootScope', 'SocketService', function ($scope, $rootScope, socket) {
    $scope.classLabel = 'col-sm-4 control-label';
    $scope.classInput = 'col-sm-8';

    $scope.range = function (start, end) {
        var array = [],
            i = start;
        for (i; i < end; i += 1) {
            array.push(i);
        }
        return array;
    };

    $scope.save = function () {
        socket
            .send('set_session', $scope.session)
            .then(
                function (message) {
                    //$scope.session = $.extend($scope.session, message.data);
                },
                function (message) {
                    $rootScope.$broadcast('message-box-open', {
                        modal: true,
                        mode: 'error',
                        content: message.data
                    });
                }
            );
    };

    $scope.$on('socket-received', function (event, message) {
        if (message.type === 'set_session'
                || message.type === 'get_session'
                || message.type === 'reset') {
            $scope.session = message.data;
        }
        $scope.$apply();
    });
}]);