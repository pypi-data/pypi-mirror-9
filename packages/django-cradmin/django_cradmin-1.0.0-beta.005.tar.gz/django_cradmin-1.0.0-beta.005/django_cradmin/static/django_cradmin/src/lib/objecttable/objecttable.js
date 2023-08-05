(function() {
  angular.module('djangoCradmin.objecttable', []).controller('CradminMultiselectObjectTableViewController', [
    '$scope', function($scope) {
      $scope.selectAllChecked = false;
      $scope.numberOfSelected = 0;
      $scope.selectedAction = null;
      $scope.setCheckboxValue = function(itemkey, value) {
        return $scope.items[itemkey] = value;
      };
      $scope.getCheckboxValue = function(itemkey) {
        return $scope.items[itemkey];
      };
      $scope.toggleAllCheckboxes = function() {
        $scope.selectAllChecked = !$scope.selectAllChecked;
        $scope.numberOfSelected = 0;
        return angular.forEach($scope.items, function(checked, itemkey) {
          $scope.setCheckboxValue(itemkey, $scope.selectAllChecked);
          if ($scope.selectAllChecked) {
            return $scope.numberOfSelected += 1;
          }
        });
      };
      return $scope.toggleCheckbox = function(itemkey) {
        var newvalue;
        newvalue = !$scope.getCheckboxValue(itemkey);
        $scope.setCheckboxValue(itemkey, newvalue);
        if (newvalue) {
          return $scope.numberOfSelected += 1;
        } else {
          $scope.numberOfSelected -= 1;
          return $scope.selectAllChecked = false;
        }
      };
    }
  ]);

}).call(this);
