(function() {
  angular.module('djangoCradmin.detectizrMockDesktop', []).factory('cradminDetectize', function() {
    return {
      device: {
        type: 'desktop'
      }
    };
  });

  angular.module('djangoCradmin.detectizrMockMobile', []).factory('cradminDetectize', function() {
    return {
      device: {
        type: 'mobile'
      }
    };
  });

  describe('djangoCradminBulkfileuploadAdvanced', function() {
    var $compile, $rootScope;
    $compile = null;
    $rootScope = null;
    beforeEach(module('djangoCradmin.bulkfileupload', 'djangoCradmin.detectizrMockDesktop'));
    beforeEach(inject(function(_$compile_, _$rootScope_) {
      $compile = _$compile_;
      return $rootScope = _$rootScope_;
    }));
    return it('should hide simple widget', function() {
      var element, html, scope;
      scope = {};
      html = "<form django-cradmin-bulkfileupload-form>\n  <div django-cradmin-bulkfileupload=\"/file_upload_api_mock\">\n    <div django-cradmin-bulkfileupload-advanced-widget id=\"advanced\"></div>\n    <div django-cradmin-bulkfileupload-simple-widget id=\"simple\"></div>\n  </div>\n</form>";
      element = $compile(html)($rootScope);
      $rootScope.$digest();
      expect(element.find('#simple').css('display')).toBe('none');
      return expect(element.find('#advanced').css('display')).toBe('');
    });
  });

  describe('djangoCradminBulkfileuploadMobile', function() {
    var $compile, $rootScope;
    $compile = null;
    $rootScope = null;
    beforeEach(module('djangoCradmin.bulkfileupload', 'djangoCradmin.detectizrMockMobile'));
    beforeEach(inject(function(_$compile_, _$rootScope_) {
      $compile = _$compile_;
      return $rootScope = _$rootScope_;
    }));
    return it('should hide advanced widget', function() {
      var element, html, scope;
      scope = {};
      html = "<form django-cradmin-bulkfileupload-form>\n  <div django-cradmin-bulkfileupload=\"/file_upload_api_mock\">\n    <div django-cradmin-bulkfileupload-advanced-widget id=\"advanced\"></div>\n    <div django-cradmin-bulkfileupload-simple-widget id=\"simple\"></div>\n  </div>\n</form>";
      element = $compile(html)($rootScope);
      $rootScope.$digest();
      expect(element.find('#simple').css('display')).toBe('');
      return expect(element.find('#advanced').css('display')).toBe('none');
    });
  });

  describe('djangoCradminBulkfileuploadInProgressOrFinished', function() {
    var $compile, $rootScope, formElement, getProgressFilenames, getProgressPercents, inProgressOrFinishedElement, inProgressOrFinishedScope;
    $compile = null;
    $rootScope = null;
    formElement = null;
    inProgressOrFinishedElement = null;
    inProgressOrFinishedScope = null;
    beforeEach(module('djangoCradmin.bulkfileupload', 'djangoCradmin.templates', 'djangoCradmin.detectizrMockDesktop'));
    beforeEach(inject(function(_$compile_, _$rootScope_) {
      var html;
      $compile = _$compile_;
      $rootScope = _$rootScope_;
      html = "<form django-cradmin-bulkfileupload-form>\n  <div django-cradmin-bulkfileupload=\"/file_upload_api_mock\">\n    <div django-cradmin-bulkfileupload-progress id=\"progress\"></div>\n  </div>\n</form>";
      formElement = $compile(html)($rootScope);
      $rootScope.$digest();
      inProgressOrFinishedElement = formElement.find('#progress');
      return inProgressOrFinishedScope = inProgressOrFinishedElement.isolateScope();
    }));
    getProgressPercents = function() {
      var domelement, elements, percent, progressPercents, _i, _len;
      progressPercents = [];
      elements = inProgressOrFinishedElement.find('.django-cradmin-progresspercent-number');
      for (_i = 0, _len = elements.length; _i < _len; _i++) {
        domelement = elements[_i];
        percent = angular.element(domelement).text().trim();
        progressPercents.push(percent);
      }
      return progressPercents;
    };
    getProgressFilenames = function() {
      var domelement, elements, filename, filenames, _i, _len;
      filenames = [];
      elements = inProgressOrFinishedElement.find('.django-cradmin-filename');
      for (_i = 0, _len = elements.length; _i < _len; _i++) {
        domelement = elements[_i];
        filename = angular.element(domelement).text().trim();
        filenames.push(filename);
      }
      return filenames;
    };
    it('should re-render when adding FileInfoList', function() {
      expect(inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item').length).toBe(0);
      inProgressOrFinishedScope.fileInfoLists.push({
        percent: 0,
        files: [
          {
            name: 'test.txt'
          }
        ]
      });
      inProgressOrFinishedScope.$apply();
      return expect(inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item').length).toBe(1);
    });
    it('should re-render when changing percent', function() {
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 0,
          files: [
            {
              name: 'test.txt'
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      expect(getProgressPercents()[0]).toBe('0');
      inProgressOrFinishedScope.fileInfoLists[0].percent = '20';
      inProgressOrFinishedScope.$apply();
      return expect(getProgressPercents()[0]).toBe('20');
    });
    it('should render files when one file in each item', function() {
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 0,
          files: [
            {
              name: 'test1.txt'
            }
          ]
        }, {
          percent: 0,
          files: [
            {
              name: 'test2.txt'
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      expect(getProgressFilenames()[0]).toBe('test1.txt');
      expect(getProgressFilenames()[1]).toBe('test2.txt');
      return expect(inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-fileinfolist').length).toBe(2);
    });
    it('should render files when multiple files in each item', function() {
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 0,
          files: [
            {
              name: 'test1.txt'
            }, {
              name: 'test2.txt'
            }
          ]
        }, {
          percent: 0,
          files: [
            {
              name: 'test3.txt'
            }, {
              name: 'test4.txt'
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      expect(getProgressFilenames()[0]).toBe('test1.txt');
      expect(getProgressFilenames()[1]).toBe('test2.txt');
      expect(getProgressFilenames()[2]).toBe('test3.txt');
      expect(getProgressFilenames()[3]).toBe('test4.txt');
      return expect(inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-fileinfolist').length).toBe(2);
    });
    it('should add finished class when finished', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          finished: true,
          files: [
            {
              name: 'test1.txt'
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      return expect(firstItem.hasClass('django-cradmin-bulkfileupload-progress-item-finished')).toBe(true);
    });
    it('should add error message on error', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          files: [
            {
              name: 'test1.txt'
            }
          ],
          hasErrors: true,
          errors: {
            file: [
              {
                message: 'File is too big'
              }
            ]
          }
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      expect(firstItem.find('.django-cradmin-bulkfileupload-error').length).toBe(1);
      return expect(firstItem.find('.django-cradmin-bulkfileupload-error').text().trim()).toBe('File is too big');
    });
    it('should add error class on error', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          files: [
            {
              name: 'test1.txt'
            }
          ],
          hasErrors: true,
          errors: {}
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      return expect(firstItem.hasClass('django-cradmin-bulkfileupload-progress-item-error')).toBe(true);
    });
    it('should show delete button when finished', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          finished: true,
          files: [
            {
              name: 'test1.txt'
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      return expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button').length).toBe(1);
    });
    it('should not show delete button when not finished', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          finished: false,
          files: [
            {
              name: 'test1.txt'
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      return expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button').length).toBe(0);
    });
    it('should not show delete button when not successful', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          finished: true,
          files: [
            {
              name: 'test1.txt'
            }
          ],
          hasErrors: true,
          errors: {}
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      return expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button').length).toBe(0);
    });
    it('should show isRemoving message when removing', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          finished: true,
          files: [
            {
              name: 'test1.txt',
              isRemoving: true
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isremoving').length).toBe(1);
      return expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isnotremoving').length).toBe(0);
    });
    return it('should not show isRemoving message when not removing', function() {
      var firstItem;
      inProgressOrFinishedScope.fileInfoLists = [
        {
          percent: 100,
          finished: true,
          files: [
            {
              name: 'test1.txt'
            }
          ]
        }
      ];
      inProgressOrFinishedScope.$apply();
      firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item');
      expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isremoving').length).toBe(0);
      return expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isnotremoving').length).toBe(1);
    });
  });

}).call(this);
