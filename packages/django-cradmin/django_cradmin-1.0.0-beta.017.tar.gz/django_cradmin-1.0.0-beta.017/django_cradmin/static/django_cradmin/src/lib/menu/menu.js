(function() {
  angular.module('djangoCradmin.menu', []).controller('CradminMenuController', function($scope) {
    $scope.displayMenu = false;
    return $scope.toggleNavigation = function() {
      return $scope.displayMenu = !$scope.displayMenu;
    };
  });

}).call(this);
