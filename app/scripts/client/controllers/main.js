/*jslint browser: true*/
/*global angular, app, $*/
'use strict';

app.controller('MainCtrl', [ '$scope', 'SocketService', '$interval', function ($scope, socket, $interval) {
    $scope.isConnected = false;
    $scope.isWaiting = false;
    $scope.instructionsVisible = false;
    $scope.timerIsRunning = false;

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
        if ($scope.isMessageBoxOpen) {
            $scope.$broadcast('message-box-close');
            return;
        }
        if ($scope.isWaiting) {
            return;
        }
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
                        mode: 'error',
                        content: message.data
                    });
                }
            );
    };

    $scope.startPriceTimer = function () {
        if ($scope.priceTimer !== null) {
            $interval.cancel($scope.priceTimer);
        }
        if ($scope.group !== null) {
            $scope.priceTimer = $interval(function () {
                if ($scope.group !== null) {
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
                }
            }, $scope.session.input_step_time * 1000, $scope.session.input_step_max);
        }
    };

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

    $scope.range = function (start, end) {
        var array = [],
            i = start;
        for (i; i < end; i += 1) {
            array.push(i);
        }
        return array;
    };

    $scope.totalValue = function (quatity) {
        var s = $scope.session,
            vs = s.AValues,
            ps = s.AValuesParamSets[s.phase.key][s.period.key];
        return vs[ps][$scope.subject.role][quatity];
    };

    $scope.incrementalValue = function (quantity) {
        var s = $scope.session,
            vus = s.AValueUp,
            ps = s.AValuesParamSets[s.phase.key][s.period.key];
        return vus[ps][$scope.subject.role][quantity - 1];
    };

    $scope.$on('socket-initialized', function (event, message) {
        $scope.isConnected = true;
        $scope.session = $.extend($scope.session, message.data.session);
        socket.send('get_subject');
    });

    $scope.$on('socket-received', function (event, message) {
        var data = null,
            title = null,
            time_left = null,
            current_price = 0;
        if (message.type === 'get_subject'
                || message.type === 'set_subject'
                || message.type === 'continue_session') {
            data = message.data;
            $scope.subject = data;
            $scope.session = data.session;
            $scope.group = data.group;
            timerClear();
            $scope.isWaiting = $scope.subject.state_name === 'waiting';
            if ($scope.subject.time_left > 0) {
                time_left = parseInt(($scope.subject.time_up - new Date().getTime()) / 1000, 10);
                if (time_left <= 0) {
                    time_left = 1;
                }
                $scope.answerCountdown = time_left;
                timerStart();
                if ($scope.group.stage === 8 || $scope.group.stage === 13) {
                    $scope.startPriceTimer();
                }
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
                current_price = ($scope.session.input_step_max * $scope.session.input_step_size) - (parseInt(time_left / $scope.session.input_step_time, 10) * $scope.session.input_step_size);
                if ($scope.subject.group.stage === 8) {
                    $scope.subject.my_bid = current_price;
                } else if ($scope.subject.group.stage === 14) {
                    $scope.subject.my_ask = current_price;
                }
            }
        }
        $scope.$apply();
    });

    $scope.$on('socket-closed', function () {
        $scope.isConnected = false;
        $scope.isWaiting = true;
        timerClear();
        $scope.$apply();
    });

    $scope.$on('$destroy', function () {
        $interval.cancel($scope.priceTimer);
    });

    $scope.$on('message-box-open', function () {
        $scope.isMessageBoxOpen = true;
    });

    $scope.$on('message-box-close', function () {
        $scope.isMessageBoxOpen = false;
    });
}]);