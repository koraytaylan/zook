/*jslint browser: true*/
/*global app*/
'use strict';

app.directive('stage0', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage0.html',
        controller: function ($scope) {
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
        }
    };
}]);

app.directive('stage2', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage2.html',
        controller: function ($scope) {
        }
    };
}]);

app.directive('stage5', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage5.html',
        controller: function ($scope) {
        }
    };
}]);

app.directive('stage7', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage7.html',
        controller: function ($scope) {
        }
    };
}]);

app.directive('stage8', [ '$timeout', function ($timeout) {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage8.html',
        controller: function ($scope, $timeout) {
            /*$timeout(function () {
                $scope.subject.price += $scope.session.input_step_size;
            }, $scope.session.input_step_time * 1000);*/
            $scope.getBid = function () {
                if ($scope.subject.my_bid < 0) {
                    return 0;
                }
                return $scope.subject.my_bid;
            };

            $scope.startPriceTimer();
        }
    };
}]);

app.directive('stage10', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage10.html',
        controller: function ($scope) {
        }
    };
}]);

app.directive('stage12', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage12.html',
        controller: function ($scope) {
        }
    };
}]);

app.directive('stage13', [ '$interval', function ($interval) {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage13.html',
        controller: function ($scope, $interval) {
            /*$scope.timer = $interval(function () {
                $scope.subject.price += $scope.session.input_step_size;
            }, $scope.session.input_step_time * 1000);

            $scope.$on('$destroy', function () {
                $interval.cancel($scope.timer);
            });*/
            $scope.getAsk = function () {
                if ($scope.subject.my_ask < 0) {
                    return 0;
                }
                return $scope.subject.my_ask;
            };

            $scope.startPriceTimer();
        }
    };
}]);

app.directive('stage15', [ function () {
    return {
        restrict: 'E',
        scope: false,
        templateUrl: 'partials/client/stage15.html',
        controller: function ($scope) {
        }
    };
}]);