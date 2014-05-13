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
                function () {
                    timerClear();
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

    $scope.$on('socket-initialized', function (event, message) {
        $scope.session = $.extend($scope.session, message.data.session);
        socket.send('get_subject');
        console.log('client socket initialized');
    });

    $scope.$on('socket-received', function (event, message) {
        console.log('client socket received', message);
        var data = null,
            title = null;
        if (message.type === 'get_subject'
                || message.type === 'set_subject'
                || message.type === 'continue_session') {
            data = message.data;
            $scope.subject = data;
            $scope.session = data.session;
            $scope.group = data.group;

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
                $scope.isInitialized = true;
                $scope.isWaiting = false;
                if ($scope.subject.time_left > 0) {
                    $scope.answerCountdown = $scope.subject.time_left;
                    timerClear();
                    timerStart();
                    if ($scope.group.stage === 8 || $scope.group.stage === 13) {
                        $scope.startPriceTimer();
                    }
                }
                break;
            case 'robot':
                $scope.isInitialized = true;
                $scope.isWaiting = true;
                timerStop();
                break;
            default:
                $scope.isWaiting = true;
                break;
            }
        }
        if ($scope.group !== null && $scope.group.stage >= 0) {
            if ($scope.session.phase !== null) {
                title = '';
                title += 'Phase: ' + $scope.session.phase.key;
                if ($scope.session.period !== null) {
                    title += ', Period: ' + $scope.session.period.key;
                    if ($scope.group !== null) {
                        title += ', Stage: ' + $scope.group.stage;
                    }
                }
                if (title !== '') {
                    $scope.title = 'Phase: ' + $scope.session.phase.key + ', Period: ' + $scope.session.period.key + ', Stage: ' + $scope.group.stage;
                }
            }
        }
        $scope.$apply();
    });

    $scope.$on('socket-closed', function () {
        $scope.isWaiting = false;
    });

    $scope.startPriceTimer = function () {
        if ($scope.priceTimer !== null) {
            $interval.cancel($scope.priceTimer);
        }
        $scope.priceTimer = $interval(function () {
            if ($scope.group.stage === 8) {
                if ($scope.subject.my_bid === -1) {
                    $scope.subject.my_bid = 0;
                }
                $scope.subject.my_bid += 0.1;
            } else if ($scope.group.stage === 13) {
                if ($scope.subject.my_ask === -1) {
                    $scope.subject.my_ask = 0;
                }
                $scope.subject.my_ask += 0.1;
            }
        }, $scope.session.input_step_time * 1000, $scope.session.input_step_max);
    };

    $scope.$on('$destroy', function () {
        $interval.cancel($scope.priceTimer);
    });

    $scope.getBid = function () {
        if ($scope.subject.my_bid < 0) {
            return 0;
        }
        return $scope.subject.my_bid;
    };
    $scope.getAsk = function () {
        if ($scope.subject.my_ask < 0) {
            return 0;
        }
        return $scope.subject.my_ask;
    };
}]);