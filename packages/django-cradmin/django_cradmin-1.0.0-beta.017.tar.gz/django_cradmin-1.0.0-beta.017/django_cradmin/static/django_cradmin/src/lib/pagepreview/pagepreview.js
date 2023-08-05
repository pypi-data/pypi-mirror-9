(function() {
  angular.module('djangoCradmin.pagepreview', []).directive('djangoCradminPagePreviewWrapper', [
    function() {
      /*
      A directive that shows a preview of a page in an iframe.
      value.
      
      Components:
      
        - A DIV using this directive (``django-cradmin-page-preview-wrapper``)
          with the following child elements:
          - A child DIV using the ``django-cradmin-page-preview-iframe-wrapper``
            directive with the following child elements:
            - A "Close" link/button using the ``django-cradmin-page-preview-iframe-closebutton`` directive.
            - A IFRAME element using the ``django-cradmin-page-preview-iframe`` directive.
          - A child element with one of the following directives:
            - ``django-cradmin-page-preview-open-on-page-load`` to show the preview when the page loads.
            - ``django-cradmin-page-preview-open-on-click`` to show the preview when the element is clicked.
      
      The outer wrapper (``django-cradmin-page-preview-wrapper``) coordinates everything.
      
      You can have one wrapper with many ``django-cradmin-page-preview-open-on-click`` directives.
      This is typically used in listings where each item in the list has its own preview button.
      Just wrap the entire list in a ``django-cradmin-page-preview-wrapper``, add the
      ``django-cradmin-page-preview-iframe-wrapper`` before the list, and a button/link with
      the ``django-cradmin-page-preview-open-on-click``-directive for each entry in the list.
      
      
      Example:
      
      ```
      <div django-cradmin-page-preview-wrapper>
          <div class="ng-hide django-cradmin-floating-fullsize-iframe-wrapper"
               django-cradmin-page-preview-iframe-wrapper>
              <a href="#" class="django-cradmin-floating-fullsize-iframe-closebutton"
                 django-cradmin-page-preview-iframe-closebutton>
                  <span class="fa fa-close"></span>
                  <span class="sr-only">Close preview</span>
              </a>
              <div class="django-cradmin-floating-fullsize-loadspinner">
                  <span class="fa fa-spinner fa-spin"></span>
              </div>
              <div class="django-cradmin-floating-fullsize-iframe-inner">
                  <iframe django-cradmin-page-preview-iframe></iframe>
              </div>
          </div>
      
          <div django-cradmin-page-preview-open-on-page-load="'/some/view'"></div>
      </div>
      ```
      */

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
          this.showPreview = function(url) {
            $scope.iframeScope.setUrl(url);
            return $scope.iframeWrapperScope.show();
          };
        },
        link: function(scope, element) {}
      };
    }
  ]).directive('djangoCradminPagePreviewOpenOnPageLoad', [
    function() {
      /*
      A directive that opens the given URL in an iframe overlay instantly (on page load).
      */

      return {
        require: '^^djangoCradminPagePreviewWrapper',
        restrict: 'A',
        scope: {
          previewUrl: '@djangoCradminPagePreviewOpenOnPageLoad'
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          wrapperCtrl.showPreview(scope.previewUrl);
        }
      };
    }
  ]).directive('djangoCradminPagePreviewOpenOnClick', [
    function() {
      /*
      A directive that opens the given URL in an iframe overlay on click.
      */

      return {
        require: '^^djangoCradminPagePreviewWrapper',
        restrict: 'A',
        scope: {
          previewUrl: '@djangoCradminPagePreviewOpenOnClick'
        },
        link: function(scope, element, attrs, wrapperCtrl) {
          element.on('click', function(e) {
            e.preventDefault();
            return wrapperCtrl.showPreview(scope.previewUrl);
          });
        }
      };
    }
  ]).directive('djangoCradminPagePreviewIframeWrapper', [
    '$window', function($window) {
      return {
        require: '^^djangoCradminPagePreviewWrapper',
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
  ]).directive('djangoCradminPagePreviewIframeClosebutton', function() {
    return {
      require: '^^djangoCradminPagePreviewIframeWrapper',
      restrict: 'A',
      scope: {},
      link: function(scope, element, attrs, iframeWrapperCtrl) {
        element.on('click', function(e) {
          e.preventDefault();
          return iframeWrapperCtrl.closeIframe();
        });
      }
    };
  }).directive('djangoCradminPagePreviewIframe', function() {
    return {
      require: '^^djangoCradminPagePreviewWrapper',
      restrict: 'A',
      scope: {},
      controller: function($scope) {
        return $scope.setUrl = function(url) {
          return $scope.element.attr('src', url);
        };
      },
      link: function(scope, element, attrs, wrapperCtrl) {
        scope.element = element;
        wrapperCtrl.setIframe(scope);
      }
    };
  });

}).call(this);
