(function() {
  angular.module('djangoCradmin.wysihtml', []).directive('djangoCradminWysihtml', function() {
    return {
      restrict: 'A',
      transclude: true,
      template: '<div><p>Stuff is awesome!</p><div ng-transclude></div></div>'
    };
  });

}).call(this);
