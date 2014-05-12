/*jslint browser: true*/
/*global angular*/
'use strict';

var app = angular.module('zook', []);

app.filter('currency', function ($filter) {
    return function (amount) {
        var isNegative = amount < 0;
        if (isNegative) {
            amount = -1 * amount;
        }
        return (isNegative ? '-$' : '$')
            + $filter('number')(amount, 2);
    };
});