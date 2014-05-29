/*jslint browser: true*/
/*global angular, app, $*/
'use strict';

app.controller('ClientsCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
    $scope.predicate = 'name';
    $scope.reverse = false;
    $scope.subjectCounts = [];

    $scope.Math = window.Math;

    var generateSubjectCounts = function () {
        var cs = [],
            ss = $scope.session.subjects;
        cs.push({
            name: 'Active',
            count: $.map(ss, function (obj) {
                if (obj.state_name === 'active') {
                    return obj;
                }
                return null;
            }).length
        });
        cs.push({
            name: 'Waiting',
            count: $.map(ss, function (obj) {
                if (obj.state_name === 'waiting') {
                    return obj;
                }
                return null;
            }).length
        });
        cs.push({
            name: 'Robot',
            count: $.map(ss, function (obj) {
                if (obj.state_name === 'robot') {
                    return obj;
                }
                return null;
            }).length
        });
        cs.push({
            name: 'Dropped',
            count: $.map(ss, function (obj) {
                if (obj.state_name === 'dropped') {
                    return obj;
                }
                return null;
            }).length
        });
        cs.push({
            name: 'Total',
            count: ss.length
        });
        return cs;
    };

    $scope.suspend = function (key) {
        $scope.isLoading = true;
        socket.send('suspend_subject', key).then(function () {
            $scope.isLoading = false;
            socket.send('get_session');
        });
    };

    $scope.getSubjects = function () {
        var ss = [];
        if (typeof($scope.session.subjects) !== 'undefined') {
            ss = $scope.session.subjects;
            ss = $.map(ss, function (obj, i) {
                if ($scope.session.is_started && obj.state <= 0) {
                    return null;
                }
                return obj;
            });
        }
        return ss;
    };

    $scope.$on('socket-received', function (event, message) {
        if (message.type === 'set_session'
                || message.type === 'get_session'
                || message.type === 'reset') {
            $scope.session = message.data;
            $scope.subjectCounts = generateSubjectCounts();
        }
        $scope.$apply();
    });

    $scope.$on('socket-initialized', function (event, message) {
        $scope.subjectCounts = generateSubjectCounts();
    });
}]);