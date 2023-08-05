(function() {
  angular.module('djangoCradmin.messages', []).controller('DjangoCradminMessagesCtrl', [
    '$scope', '$timeout', function($scope, $timeout) {
      $scope.loading = true;
      $timeout(function() {
        return $scope.loading = false;
      }, 650);
      $scope.messageHidden = {};
      $scope.hideMessage = function(index) {
        return $scope.messageHidden[index] = true;
      };
      $scope.messageIsHidden = function(index) {
        return $scope.messageHidden[index];
      };
    }
  ]);

}).call(this);
