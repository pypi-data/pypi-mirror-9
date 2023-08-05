(function() {
  describe('djangoCradminImagePreviewImg', function() {
    var $compile, $rootScope;
    $compile = null;
    $rootScope = null;
    beforeEach(module('djangoCradmin.imagepreview'));
    beforeEach(inject(function(_$compile_, _$rootScope_) {
      $compile = _$compile_;
      return $rootScope = _$rootScope_;
    }));
    it('should hide IMG if no src', function() {
      var element, html, scope;
      scope = {};
      html = "<div django-cradmin-image-preview>\n  <img django-cradmin-image-preview-img>\n  <input type=\"file\" name=\"myfile\" django-cradmin-image-preview-filefield>\n</div>";
      element = $compile(html)($rootScope);
      $rootScope.$digest();
      return expect(element.find('img').hasClass('ng-hide')).toBe(true);
    });
    return it('should show IMG if src', function() {
      var element, html, scope;
      scope = {};
      html = "<div django-cradmin-image-preview>\n  <img django-cradmin-image-preview-img src=\"hello.png\">\n  <input type=\"file\" name=\"myfile\" django-cradmin-image-preview-filefield>\n</div>";
      element = $compile(html)($rootScope);
      $rootScope.$digest();
      return expect(element.find('img').hasClass('ng-hide')).toBe(false);
    });
  });

}).call(this);
