(function() {
  angular.module('djangoCradmin.forms.modelchoicefield', []).directive('djangoCradminModelChoiceFieldWrapper', [
    '$window', function($window) {
      return {
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.origin = "" + window.location.protocol + "//" + window.location.host;
          this.setIframeWrapper = function(iframeWrapperScope) {
            return $scope.iframeWrapperScope = iframeWrapperScope;
          };
          this.setIframe = function(iframeScope) {
            return $scope.iframeScope = iframeScope;
          };
          this.setField = function(fieldScope) {
            return $scope.fieldScope = fieldScope;
          };
          this.setPreviewElement = function(previewElementScope) {
            return $scope.previewElementScope = previewElementScope;
          };
          this.onChangeValueBegin = function() {
            $scope.iframeScope.reset();
            return $scope.iframeWrapperScope.show();
          };
          $scope.onChangeValue = function(event) {
            var data;
            if (event.origin !== $scope.origin) {
              console.error("Message origin '" + event.origin + "' does not match current origin '" + $scope.origin + "'.");
              return;
            }
            data = angular.fromJson(event.data);
            if ($scope.fieldScope.fieldid !== data.fieldid) {
              return;
            }
            $scope.fieldScope.setValue(data.value);
            $scope.previewElementScope.setPreviewHtml(data.preview);
            $scope.iframeWrapperScope.hide();
            return $scope.iframeScope.clear();
          };
          $window.addEventListener('message', $scope.onChangeValue, false);
        },
        link: function(scope, element) {}
      };
    }
  ]).directive('djangoCradminModelChoiceFieldInput', function() {
    return {
      require: '^djangoCradminModelChoiceFieldWrapper',
      restrict: 'A',
      scope: {},
      controller: function($scope) {
        $scope.setValue = function(value) {
          return $scope.inputElement.val(value);
        };
      },
      link: function(scope, element, attrs, wrapperCtrl) {
        scope.inputElement = element;
        scope.fieldid = attrs['id'];
        wrapperCtrl.setField(scope);
      }
    };
  }).directive('djangoCradminModelChoiceFieldPreview', function() {
    return {
      require: '^djangoCradminModelChoiceFieldWrapper',
      restrict: 'A',
      scope: {},
      controller: function($scope) {
        $scope.setPreviewHtml = function(previewHtml) {
          return $scope.previewElement.html(previewHtml);
        };
      },
      link: function(scope, element, attrs, wrapperCtrl) {
        scope.previewElement = element;
        wrapperCtrl.setPreviewElement(scope);
      }
    };
  }).directive('djangoCradminModelChoiceFieldChangebeginButton', function() {
    return {
      require: '^djangoCradminModelChoiceFieldWrapper',
      restrict: 'A',
      scope: {},
      link: function(scope, element, attrs, wrapperCtrl) {
        element.on('click', function(e) {
          e.preventDefault();
          return wrapperCtrl.onChangeValueBegin();
        });
      }
    };
  }).directive('djangoCradminModelChoiceFieldIframeWrapper', [
    '$window', function($window) {
      return {
        require: '^djangoCradminModelChoiceFieldWrapper',
        restrict: 'A',
        scope: {},
        controller: function($scope) {
          $scope.bodyElement = angular.element($window.document.body);
          $scope.show = function() {
            $scope.iframeWrapperElement.removeClass('ng-hide');
            return $scope.bodyElement.addClass('django-cradmin-noscroll');
          };
          $scope.hide = function() {
            $scope.iframeWrapperElement.addClass('ng-hide');
            return $scope.bodyElement.removeClass('django-cradmin-noscroll');
          };
          this.closeIframe = function() {
            return $scope.hide();
          };
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          scope.iframeWrapperElement = element;
          wrapperCtrl.setIframeWrapper(scope);
        }
      };
    }
  ]).directive('djangoCradminModelChoiceFieldIframeClosebutton', function() {
    return {
      require: '^djangoCradminModelChoiceFieldIframeWrapper',
      restrict: 'A',
      scope: {},
      link: function(scope, element, attrs, iframeWrapperCtrl) {
        element.on('click', function(e) {
          e.preventDefault();
          return iframeWrapperCtrl.closeIframe();
        });
      }
    };
  }).directive('djangoCradminModelChoiceFieldIframe', function() {
    return {
      require: '^djangoCradminModelChoiceFieldWrapper',
      restrict: 'A',
      scope: {
        src: '@djangoCradminModelChoiceFieldIframe'
      },
      controller: function($scope) {
        $scope.clear = function() {
          return $scope.element.attr('src', '');
        };
        return $scope.reset = function() {
          return $scope.element.attr('src', $scope.src);
        };
      },
      link: function(scope, element, attrs, wrapperCtrl) {
        scope.element = element;
        wrapperCtrl.setIframe(scope);
      }
    };
  });

}).call(this);
