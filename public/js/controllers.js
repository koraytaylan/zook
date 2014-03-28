var app = angular.module('zook', []);
 
app.controller('MainCtrl', [ '$scope', 'SocketService', function ($scope, socket) {
	$scope.getYourName = function () {
		return $scope.yourName;
	}

	$scope.sendMessage = function () {
        socket.echo($scope.txtYourName).then(function (message) {
            $scope.yourName = message.data;
        });
	}

    socket.onInitialize(function () {
        socket.send('echo');
    });
    
}]);