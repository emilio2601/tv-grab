var radioApp = angular.module("radioApp", []);

radioApp.controller("scheduleCtrl", function($scope, $http){
	scope = $scope
	$scope.ver = "0.10"

	$scope.input = {
		"format": "raw",
		"channel": "XHBZ"}

	$scope.submit= function(){
		$scope.sched_to_send = {
			date_start: js_date_to_py($scope.input.date_start),
			format: $scope.input.format,
			title: $scope.input.title,
			tunerId: 1,
			channel: $scope.input.channel,
			duration: ($scope.input.hours * 60 * 60) + ($scope.input.minutes * 60) + $scope.input.seconds
		};

		console.log($scope.sched_to_send)

		$http.post("radio/api/v1/schedule", $scope.sched_to_send).then(function(res){
			$scope.response = res
			$scope.update()
		});

	}

	$scope.update = function (){
		$http.get("radio/api/v1/schedule").then(function(res){
		$scope.sched = res.data.recordings
		for (var i = $scope.sched.length - 1; i >= 0; i--) {
			$scope.sched[i].date_start = moment($scope.sched[i].date_start[0] + " " + $scope.sched[i].date_start[1]).format("dddd, MMMM Do YYYY, h:mm:ss a");
			$scope.sched[i].date_end = moment($scope.sched[i].date_end[0] + " " + $scope.sched[i].date_end[1]).format("dddd, MMMM Do YYYY, h:mm:ss a");
		}

		});
	}

	$scope.update()



	});
 
function js_date_to_py(date){
	dateArr = ["",""]
	dateArr[0] = moment(date).format("YYYY-MM-DD");
	dateArr[1] = moment(date).format("HH:mm:ss");
	return dateArr	
}
