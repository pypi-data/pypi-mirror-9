(function() {
  angular.module('djangoCradmin.imagepreview', []).directive('djangoCradminImagePreview', function() {
    /*
    A directive that shows a preview when an image field changes
    value.
    
    Components:
      - A wrapper (typically a DIV) using this directive (``django-cradmin-image-preview``)
      - An IMG element using the ``django-cradmin-image-preview-img`` directive. This is
        needed even if we have no initial image.
      - A file input field using the ``django-cradmin-image-preview-filefield`` directive.
    
    Example:
    
      <div django-cradmin-image-preview>
        <img django-cradmin-image-preview-img>
        <input type="file" name="myfile" django-cradmin-image-preview-filefield>
      </div>
    */

    var controller;
    controller = function($scope) {
      this.setImg = function(imgscope) {
        return $scope.img = imgscope;
      };
      this.previewFile = function(file) {
        return $scope.img.previewFile(file);
      };
    };
    return {
      restrict: 'A',
      scope: {},
      controller: controller
    };
  }).directive('djangoCradminImagePreviewImg', function() {
    var controller, link, onFilePreviewLoaded;
    onFilePreviewLoaded = function($scope, srcData) {
      $scope.element.attr('height', '');
      $scope.element[0].src = srcData;
      return $scope.element.removeClass('ng-hide');
    };
    controller = function($scope) {
      $scope.previewFile = function(file) {
        var reader;
        reader = new FileReader();
        reader.onload = function(evt) {
          return onFilePreviewLoaded($scope, evt.target.result);
        };
        return reader.readAsDataURL(file);
      };
    };
    link = function(scope, element, attrs, previewCtrl) {
      scope.element = element;
      previewCtrl.setImg(scope);
      if ((element.attr('src') == null) || element.attr('src') === '') {
        element.addClass('ng-hide');
      }
    };
    return {
      require: '^djangoCradminImagePreview',
      restrict: 'A',
      scope: {},
      controller: controller,
      link: link
    };
  }).directive('djangoCradminImagePreviewFilefield', function() {
    var link;
    link = function(scope, element, attrs, previewCtrl) {
      scope.previewCtrl = previewCtrl;
      scope.element = element;
      scope.wrapperelement = element.parent();
      element.bind('change', function(evt) {
        var file;
        if (evt.target.files != null) {
          file = evt.target.files[0];
          return scope.previewCtrl.previewFile(file);
        }
      });
      element.bind('mouseover', function() {
        return scope.wrapperelement.addClass('django_cradmin_filewidget_field_and_overlay_wrapper_hover');
      });
      element.bind('mouseleave', function() {
        return scope.wrapperelement.removeClass('django_cradmin_filewidget_field_and_overlay_wrapper_hover');
      });
    };
    return {
      require: '^djangoCradminImagePreview',
      restrict: 'A',
      scope: {},
      link: link
    };
  });

}).call(this);
