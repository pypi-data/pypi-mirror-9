(function() {
  angular.module('djangoCradmin.detectizr', []).factory('cradminDetectize', function() {
    Detectizr.detect({
      addAllFeaturesAsClass: false,
      detectDevice: true,
      detectDeviceModel: false,
      detectScreen: false,
      detectOS: false,
      detectBrowser: false,
      detectPlugins: false
    });
    return Detectizr;
  });

}).call(this);
