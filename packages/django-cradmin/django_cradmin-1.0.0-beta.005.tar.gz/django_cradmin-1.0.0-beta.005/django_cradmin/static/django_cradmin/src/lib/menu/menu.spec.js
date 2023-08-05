(function() {
  describe('CradminMenuController', function() {
    beforeEach(module('djangoCradmin.menu'));
    return it('should start toggle displayMenu attribute', inject(function($controller) {
      var ctrl, scope;
      scope = {};
      ctrl = $controller('CradminMenuController', {
        $scope: scope
      });
      expect(scope.displayMenu).toBe(false);
      scope.toggleNavigation();
      expect(scope.displayMenu).toBe(true);
      scope.toggleNavigation();
      return expect(scope.displayMenu).toBe(false);
    }));
  });

}).call(this);
