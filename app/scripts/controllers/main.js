/*jslint browser: true*/
/*global angular, app*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.isLoading = true;
    $scope.isInitialized = false;
    $scope.instructionsVisible = false;
    $scope.timerIsRunning = false;

    $scope.title = 'Welcome to Zook!';
    $scope.subject = null;
    $scope.answerCountdown = 60;

    $scope.state = 0;
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
        $scope.$broadcast('continue');
    };

    socket.onInitialize(function () {
        socket.send('get_subject').then(function (message) {
            $scope.subject = message.data;
            $scope.isLoading = false;
            $scope.toggleTimer();
        });
    });
}]);