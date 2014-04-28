/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', 'LogService', function ($scope, socket, log) {
    $scope.status = 'passive';
    $scope.isInitialized = false;
    $scope.instructionsVisible = false;
    $scope.timerIsRunning = false;
    $scope.isWaiting = false;
    $scope.isInitialized = false;

    $scope.title = 'Welcome to Zook!';
    $scope.subject = null;
    $scope.answerCountdown = 60;

    $scope.state = -1;
    $scope.clientNameInvalid = false;

    var timerId = null,
        timerTicks = 0,
        timerFinished = true,
        timerStop = function () {
            $scope.timerIsRunning = false;
            if (timerId !== null) {
                clearTimeout(timerId);
                timerId = null;
            }
        },
        timerFinish = function () {
            $scope.timerIsRunning = false;
            timerFinished = true;
            timerStop();
        },
        timerTick = function () {
            $scope.timerIsRunning = true;
            timerTicks -= 1;
            if (timerTicks > 0) {
                timerId = setTimeout(function () {
                    timerTick();
                    $scope.$apply();
                }, 1000);
            } else {
                timerFinish();
            }
        },
        timerStart = function () {
            if (timerFinished) {
                timerTicks = $scope.answerCountdown;
            }
            timerFinished = false;
            timerTick();
        };

    $scope.getYourName = function () {
        return $scope.yourName;
    };

    $scope.sendMessage = function () {
        socket.echo($scope.txtYourName).then(function (message) {
            $scope.yourName = message.data;
        });
    };

    $scope.toggleTimer = function () {
        if ($scope.timerIsRunning) {
            timerStop();
        } else {
            timerStart();
        }
    };

    $scope.clearTimer = function () {
        timerStop();
        timerTicks = $scope.answerCountdown;
    };

    $scope.getRemainingTime = function () {
        return timerTicks;
    };

    $scope.continue = function () {
        $scope.isWaiting = true;
        $scope.$broadcast('continue');
    };

    $scope.$on('state-waiting', function () {
        $scope.state = -1;
        $scope.isWaiting = true;
    });

    $scope.$on('state-initial', function () {
        $scope.state = 0;
        $scope.isWaiting = false;
    });

    $scope.$on('socket-initialized', function (event, message) {
        var data = message.data;
        $scope.clientKey = data.key;
        $scope.session = data.session;

        socket.send('get_subject').then(function (message) {
            var s = message.data;
            if (s !== null) {
                $scope.state = s.state;
                $scope.state_name = s.state_name;
                $scope.name = s.name;
                switch ($scope.state_name) {
                case 'initial':
                    $scope.isInitialized = false;
                    $scope.isWaiting = false;
                    break;
                case 'active':
                case 'waiting':
                    $scope.isInitialized = true;
                    $scope.isWaiting = true;
                    break;
                default:
                    $scope.isWaiting = true;
                    break;
                }
            }
        });
    });

    $scope.$on('socket-closed', function (message) {
        $scope.isWaiting = false;
    });
}]);