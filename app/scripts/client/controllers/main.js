/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', 'LogService', function ($scope, socket, log) {
    $scope.status = 'passive';
    $scope.isInitialized = false;
    $scope.instructionsVisible = false;
    $scope.timerIsRunning = false;

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
        log.info('Event: MainController <- state-waiting');
        $scope.state = -1;
        $scope.isWaiting = true;
    });

    $scope.$on('state-initial', function () {
        log.info('Event: MainController <- state-initial');
        $scope.state = 0;
        $scope.isWaiting = false;
    });

    $scope.$on('socket-initialize', function (event, message) {
        var data = message.data;
        $scope.clientKey = data.key;
        $scope.session = data.session;

        socket.send('get_subject').then(function (message) {
            var s = message.data;
            if (s !== null) {
                $scope.status = s.status;
                $scope.name = s.name;
                switch ($scope.status) {
                case 'active':
                case 'waiting':
                    $scope.state = -1;
                    break;
                default:
                    $scope.state = 0;
                    break;
                }
            }
        });
    });
}]);