/*jslint browser: true*/
/*global angular, app, $*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', 'LogService', '$interval', function ($scope, socket, log, $interval) {
    $scope.status = 'passive';
    $scope.isInitialized = false;
    $scope.instructionsVisible = false;
    $scope.timerIsRunning = false;
    $scope.isWaiting = false;
    $scope.isActive = false;

    $scope.title = 'Welcome to Zook!';
    $scope.subject = {};
    $scope.session = {};
    $scope.group = {};
    $scope.answerCountdown = 60;

    $scope.clientNameInvalid = false;

    $scope.priceTimer = null;

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
        timerClear = function () {
            timerStop();
            timerTicks = $scope.answerCountdown;
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
            if (!$scope.timerIsRunning) {
                if (timerFinished) {
                    timerTicks = $scope.answerCountdown;
                }
                timerFinished = false;
                timerTick();
            }
        };

    $scope.toggleTimer = function () {
        if ($scope.timerIsRunning) {
            timerStop();
        } else {
            timerStart();
        }
    };

    $scope.getRemainingTime = function () {
        return timerTicks;
    };

    $scope.continue = function () {
        $scope.isWaiting = true;
        localStorage.setItem('subject.name', $scope.subject.name);
        socket
            .send('continue_session', $scope.subject)
            .then(
                function (message) {
                    var data = message.data;
                    timerClear();
                    $scope.session = $.extend($scope.session, data.session);
                    $scope.subject = $.extend($scope.subject, data.subject);
                },
                function (message) {
                    $scope.isWaiting = false;
                    $scope.$broadcast('message-box-open', {
                        modal: true,
                        content: message.data
                    });
                }
            );
    };

    $scope.testMessageBox = function () {
        $scope.$broadcast('message-box', {
            title: 'Test title',
            content: 'Test content',
            modal: true
        });
    };

    $scope.$on('socket-initialized', function (event, message) {
        $scope.session = $.extend($scope.session, message.data.session);
        socket
            .send('get_subject')
            .then(function () {
                socket
                    .send('get_session')
                    .then(function () {
                        socket
                            .send('get_group');
                    });
            });
    });

    $scope.$on('socket-received', function (event, message) {
        if (message.type === 'get_subject'
                || message.type === 'set_subject') {
            var s = message.data;
            $scope.subject = $.extend($scope.subject, s);
        } else if (message.type === 'get_session') {
            $scope.session = $.extend($scope.session, message.data);
        } else if (message.type === 'get_group') {
            $scope.group = $.extend($scope.group, message.data);
        } else if (message.type === 'continue_session') {
            var data = message.data;
            $scope.subject = $.extend($scope.subject, data.subject);
            $scope.session = $.extend($scope.session, data.session);
            $scope.group = $.extend($scope.group, data.group);
        }
        switch ($scope.subject.state_name) {
        case 'initial':
            $scope.isInitialized = false;
            $scope.isWaiting = false;
            break;
        case 'waiting':
            $scope.isInitialized = true;
            $scope.isWaiting = true;
            timerStop();
            break;
        case 'active':
            //console.log('active');
            $scope.isInitialized = true;
            $scope.isWaiting = false;
            if ($scope.subject.time_left > 0) {
                $scope.answerCountdown = $scope.subject.time_left;
                timerClear();
                timerStart();
            }
            break;
        default:
            $scope.isWaiting = true;
            break;
        }
        $scope.$apply();
    });

    $scope.$on('socket-closed', function () {
        $scope.isWaiting = false;
    });

    $scope.$watch('subject', function (newValue, oldValue) {
        console.log('watch subject', $scope.subject);
        
    });

    $scope.$watch('group.stage', function () {
        if ($scope.group.stage >= 0) {
            $scope.title = 'Phase: ' + $scope.session.phase + ', Period: ' + $scope.session.period + ', Stage: ' + $scope.group.stage;
        }
    });

    $scope.startPriceTimer = function () {
        if ($scope.priceTimer !== null) {
            $interval.cancel($scope.priceTimer);
        }
        $scope.priceTimer = $interval(function () {
            $scope.subject.price += 0.1;
        }, $scope.session.input_step_time * 1000, $scope.session.input_step_max);
    };

    $scope.$on('$destroy', function () {
        $interval.cancel($scope.priceTimer);
    });
}]);