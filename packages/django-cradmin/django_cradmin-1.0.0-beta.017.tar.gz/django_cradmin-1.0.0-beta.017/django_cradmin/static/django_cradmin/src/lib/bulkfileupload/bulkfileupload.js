(function() {
  angular.module('djangoCradmin.bulkfileupload', ['angularFileUpload', 'ngCookies']).factory('cradminBulkfileupload', function() {
    var FileInfo, FileInfoList;
    FileInfo = (function() {
      function FileInfo(options) {
        this.file = options.file;
        this.temporaryfileid = options.temporaryfileid;
        this.name = this.file.name;
        this.isRemoving = false;
      }

      FileInfo.prototype.markAsIsRemoving = function() {
        return this.isRemoving = true;
      };

      FileInfo.prototype.markAsIsNotRemoving = function() {
        return this.isRemoving = false;
      };

      return FileInfo;

    })();
    FileInfoList = (function() {
      function FileInfoList(options) {
        var file, _i, _len, _ref;
        this.percent = options.percent;
        if (options.finished) {
          this.finished = true;
        } else {
          this.finished = false;
        }
        if (options.hasErrors) {
          this.hasErrors = true;
        } else {
          this.hasErrors = false;
        }
        this.rawFiles = options.files;
        this.files = [];
        _ref = options.files;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          file = _ref[_i];
          this.files.push(new FileInfo({
            temporaryfileid: null,
            name: file.name,
            file: file
          }));
        }
        this.errors = options.errors;
      }

      FileInfoList.prototype.updatePercent = function(percent) {
        return this.percent = percent;
      };

      FileInfoList.prototype.finish = function(temporaryfiles) {
        var index, temporaryfile, _i, _len, _results;
        this.finished = true;
        index = 0;
        _results = [];
        for (_i = 0, _len = temporaryfiles.length; _i < _len; _i++) {
          temporaryfile = temporaryfiles[_i];
          this.files[index].name = temporaryfile.filename;
          this.files[index].temporaryfileid = temporaryfile.id;
          _results.push(index += 1);
        }
        return _results;
      };

      FileInfoList.prototype.setErrors = function(errors) {
        this.hasErrors = true;
        return this.errors = errors;
      };

      FileInfoList.prototype.indexOf = function(fileInfo) {
        return this.files.indexOf(fileInfo);
      };

      FileInfoList.prototype.remove = function(index) {
        return this.files.splice(index, 1);
      };

      return FileInfoList;

    })();
    return {
      createFileInfoList: function(options) {
        return new FileInfoList(options);
      }
    };
  }).directive('djangoCradminBulkfileuploadForm', [
    function() {
      /*
      A form containing ``django-cradmin-bulkfileupload`` fields
      must use this directive.
      */

      return {
        restrict: 'AE',
        scope: {},
        controller: function($scope) {
          $scope._inProgressCounter = 0;
          $scope._submitButtonScopes = [];
          $scope._setSubmitButtonsInProgress = function() {
            var buttonScope, _i, _len, _ref, _results;
            _ref = $scope._submitButtonScopes;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              buttonScope = _ref[_i];
              _results.push(buttonScope.setNotInProgress());
            }
            return _results;
          };
          $scope._setSubmitButtonsNotInProgress = function() {
            var buttonScope, _i, _len, _ref, _results;
            _ref = $scope._submitButtonScopes;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              buttonScope = _ref[_i];
              _results.push(buttonScope.setInProgress());
            }
            return _results;
          };
          this.addInProgress = function() {
            $scope._inProgressCounter += 1;
            if ($scope._inProgressCounter === 1) {
              return $scope._setSubmitButtonsInProgress();
            }
          };
          this.removeInProgress = function() {
            if ($scope._inProgressCounter === 0) {
              throw new Error("It should not be possible to get _inProgressCounter below 0");
            }
            $scope._inProgressCounter -= 1;
            if ($scope._inProgressCounter === 0) {
              return $scope._setSubmitButtonsNotInProgress();
            }
          };
          this.addSubmitButtonScope = function(submitButtonScope) {
            return $scope._submitButtonScopes.push(submitButtonScope);
          };
        },
        link: function(scope, element, attr, uploadController) {
          element.on('submit', function(evt) {
            if (scope._inProgressCounter !== 0) {
              return evt.preventDefault();
            }
          });
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadSubmit', [
    function() {
      return {
        require: '^djangoCradminBulkfileuploadForm',
        restrict: 'A',
        scope: true,
        controller: function($scope) {
          $scope.inProgress = false;
          $scope.setInProgress = function() {
            $scope.element.prop('disabled', false);
            return $scope.inProgress = false;
          };
          return $scope.setNotInProgress = function() {
            $scope.element.prop('disabled', true);
            return $scope.inProgress = true;
          };
        },
        link: function(scope, element, attr, formController) {
          scope.element = element;
          formController.addSubmitButtonScope(scope);
        }
      };
    }
  ]).directive('djangoCradminBulkfileupload', [
    '$upload', '$cookies', 'cradminDetectize', function($upload, $cookies, cradminDetectize) {
      return {
        require: '^djangoCradminBulkfileuploadForm',
        restrict: 'AE',
        scope: true,
        controller: function($scope) {
          $scope.collectionid = null;
          $scope.cradminLastFilesSelectedByUser = [];
          $scope.fileUploadQueue = [];
          $scope.firstUploadInProgress = false;
          $scope.simpleWidgetScope = null;
          $scope.advancedWidgetScope = null;
          $scope.rejectedFilesScope = null;
          this.setInProgressOrFinishedScope = function(inProgressOrFinishedScope) {
            return $scope.inProgressOrFinishedScope = inProgressOrFinishedScope;
          };
          this.setFileUploadFieldScope = function(fileUploadFieldScope) {
            return $scope.fileUploadFieldScope = fileUploadFieldScope;
          };
          this.setSimpleWidgetScope = function(simpleWidgetScope) {
            $scope.simpleWidgetScope = simpleWidgetScope;
            return $scope._showAppropriateWidget();
          };
          this.setAdvancedWidgetScope = function(advancedWidgetScope) {
            $scope.advancedWidgetScope = advancedWidgetScope;
            return $scope._showAppropriateWidget();
          };
          this.setRejectFilesScope = function(rejectedFilesScope) {
            return $scope.rejectedFilesScope = rejectedFilesScope;
          };
          this.getUploadUrl = function() {
            return $scope.uploadUrl;
          };
          this.getCollectionId = function() {
            return $scope.collectionid;
          };
          $scope._addFileInfoList = function(fileInfoList) {
            return $scope.inProgressOrFinishedScope.addFileInfoList(fileInfoList);
          };
          $scope._showAppropriateWidget = function() {
            if ($scope.advancedWidgetScope && $scope.simpleWidgetScope) {
              if (cradminDetectize.device.type === 'desktop') {
                return $scope.simpleWidgetScope.hide();
              } else {
                return $scope.advancedWidgetScope.hide();
              }
            }
          };
          $scope.filesDropped = function(files, evt, rejectedFiles) {
            if (rejectedFiles.length > 0) {
              return $scope.rejectedFilesScope.setRejectedFiles(rejectedFiles);
            }
          };
          $scope.$watch('cradminLastFilesSelectedByUser', function() {
            if ($scope.cradminLastFilesSelectedByUser.length > 0) {
              $scope._addFilesToQueue($scope.cradminLastFilesSelectedByUser.slice());
              return $scope.cradminLastFilesSelectedByUser = [];
            }
          });
          $scope._addFilesToQueue = function(files) {
            var progressInfo;
            progressInfo = $scope.inProgressOrFinishedScope.addFileInfoList({
              percent: 0,
              files: files
            });
            $scope.fileUploadQueue.push(progressInfo);
            if ($scope.firstUploadInProgress) {
              return;
            }
            if ($scope.collectionid === null) {
              $scope.firstUploadInProgress = true;
            }
            return $scope._processFileUploadQueue();
          };
          $scope._onFileUploadComplete = function() {
            /*
            Called both on file upload success and error
            */

            $scope.firstUploadInProgress = false;
            $scope.formController.removeInProgress();
            if ($scope.fileUploadQueue.length > 0) {
              return $scope._processFileUploadQueue();
            }
          };
          $scope._processFileUploadQueue = function() {
            var apidata, progressInfo;
            progressInfo = $scope.fileUploadQueue.shift();
            apidata = angular.extend({}, $scope.apiparameters, {
              collectionid: $scope.collectionid
            });
            $scope.formController.addInProgress();
            return $scope.upload = $upload.upload({
              url: $scope.uploadUrl,
              method: 'POST',
              data: apidata,
              file: progressInfo.rawFiles,
              fileFormDataName: 'file',
              headers: {
                'X-CSRFToken': $cookies.csrftoken,
                'Content-Type': 'multipart/form-data'
              }
            }).progress(function(evt) {
              return progressInfo.updatePercent(parseInt(100.0 * evt.loaded / evt.total));
            }).success(function(data, status, headers, config) {
              progressInfo.finish(data.temporaryfiles);
              $scope._setCollectionId(data.collectionid);
              return $scope._onFileUploadComplete();
            }).error(function(data) {
              progressInfo.setErrors(data);
              return $scope._onFileUploadComplete();
            });
          };
          $scope._setCollectionId = function(collectionid) {
            $scope.collectionid = collectionid;
            return $scope.fileUploadFieldScope.setCollectionId(collectionid);
          };
        },
        link: function(scope, element, attr, formController) {
          scope.uploadUrl = attr.djangoCradminBulkfileupload;
          if (attr.djangoCradminBulkfileuploadApiparameters != null) {
            scope.apiparameters = scope.$parent.$eval(attr.djangoCradminBulkfileuploadApiparameters);
            if (!angular.isObject(scope.apiparameters)) {
              throw new Error('django-cradmin-bulkfileupload-apiparameters must be a javascript object.');
            }
          } else {
            scope.apiparameters = {};
          }
          scope.formController = formController;
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadRejectedFiles', [
    function() {
      /*
      This directive is used to show files that are rejected on drop because
      of wrong mimetype. Each time a user drops one or more file with invalid
      mimetype, this template is re-rendered and displayed.
      */

      return {
        restrict: 'A',
        require: '^djangoCradminBulkfileupload',
        templateUrl: 'bulkfileupload/rejectedfiles.tpl.html',
        transclude: true,
        scope: {
          rejectedFileErrorMessage: '@djangoCradminBulkfileuploadRejectedFiles'
        },
        controller: function($scope) {
          $scope.rejectedFiles = [];
          $scope.setRejectedFiles = function(rejectedFiles) {
            return $scope.rejectedFiles = rejectedFiles;
          };
          return $scope.closeMessage = function(rejectedFile) {
            var index;
            index = $scope.rejectedFiles.indexOf(rejectedFile);
            if (index !== -1) {
              return $scope.rejectedFiles.splice(index, 1);
            }
          };
        },
        link: function(scope, element, attr, bulkfileuploadController) {
          bulkfileuploadController.setRejectFilesScope(scope);
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadProgress', [
    'cradminBulkfileupload', '$http', '$cookies', function(cradminBulkfileupload, $http, $cookies) {
      return {
        restrict: 'AE',
        require: '^djangoCradminBulkfileupload',
        templateUrl: 'bulkfileupload/progress.tpl.html',
        scope: {},
        controller: function($scope) {
          $scope.fileInfoLists = [];
          $scope._findFileInfo = function(fileInfo) {
            var fileInfoIndex, fileInfoList, _i, _len, _ref;
            if (fileInfo.temporaryfileid == null) {
              throw new Error("Can not remove files without a temporaryfileid");
            }
            _ref = $scope.fileInfoLists;
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              fileInfoList = _ref[_i];
              fileInfoIndex = fileInfoList.indexOf(fileInfo);
              if (fileInfoIndex !== -1) {
                return {
                  fileInfoList: fileInfoList,
                  index: fileInfoIndex
                };
              }
            }
            throw new Error("Could not find requested fileInfo with temporaryfileid=" + fileInfo.temporaryfileid + ".");
          };
          this.removeFile = function(fileInfo) {
            var fileInfoLocation;
            fileInfoLocation = $scope._findFileInfo(fileInfo);
            fileInfo.markAsIsRemoving();
            $scope.$apply();
            return $http({
              url: $scope.uploadController.getUploadUrl(),
              method: 'DELETE',
              headers: {
                'X-CSRFToken': $cookies.csrftoken
              },
              data: {
                collectionid: $scope.uploadController.getCollectionId(),
                temporaryfileid: fileInfo.temporaryfileid
              }
            }).success(function(data, status, headers, config) {
              return fileInfoLocation.fileInfoList.remove(fileInfoLocation.index);
            }).error(function(data, status, headers, config) {
              if (typeof console !== "undefined" && console !== null) {
                if (typeof console.error === "function") {
                  console.error('ERROR', data);
                }
              }
              alert('An error occurred while removing the file. Please try again.');
              return fileInfo.markAsIsNotRemoving();
            });
          };
          $scope.addFileInfoList = function(options) {
            var fileInfoList;
            fileInfoList = cradminBulkfileupload.createFileInfoList(options);
            $scope.fileInfoLists.push(fileInfoList);
            return fileInfoList;
          };
        },
        link: function(scope, element, attr, uploadController) {
          scope.uploadController = uploadController;
          uploadController.setInProgressOrFinishedScope(scope);
        }
      };
    }
  ]).directive('djangoCradminBulkFileInfoList', [
    function() {
      return {
        restrict: 'AE',
        scope: {
          fileInfoList: '=djangoCradminBulkFileInfoList'
        },
        templateUrl: 'bulkfileupload/fileinfolist.tpl.html',
        transclude: true,
        controller: function($scope) {
          this.close = function() {
            return $scope.element.remove();
          };
        },
        link: function(scope, element, attr) {
          scope.element = element;
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadErrorCloseButton', [
    function() {
      return {
        restrict: 'A',
        require: '^djangoCradminBulkFileInfoList',
        scope: {},
        link: function(scope, element, attr, fileInfoListController) {
          element.on('click', function(evt) {
            evt.preventDefault();
            return fileInfoListController.close();
          });
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadRemoveFileButton', [
    function() {
      return {
        restrict: 'A',
        require: '^djangoCradminBulkfileuploadProgress',
        scope: {
          'fileInfo': '=djangoCradminBulkfileuploadRemoveFileButton'
        },
        link: function(scope, element, attr, progressController) {
          element.on('click', function(evt) {
            evt.preventDefault();
            return progressController.removeFile(scope.fileInfo);
          });
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadCollectionidField', [
    function() {
      return {
        require: '^djangoCradminBulkfileupload',
        restrict: 'AE',
        scope: {},
        controller: function($scope) {
          $scope.setCollectionId = function(collectionid) {
            return $scope.element.val("" + collectionid);
          };
        },
        link: function(scope, element, attr, uploadController) {
          scope.element = element;
          uploadController.setFileUploadFieldScope(scope);
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadAdvancedWidget', [
    function() {
      return {
        require: '^djangoCradminBulkfileupload',
        restrict: 'AE',
        scope: {},
        link: function(scope, element, attr, uploadController) {
          scope.hide = function() {
            return element.css('display', 'none');
          };
          uploadController.setAdvancedWidgetScope(scope);
        }
      };
    }
  ]).directive('djangoCradminBulkfileuploadSimpleWidget', [
    function() {
      return {
        require: '^djangoCradminBulkfileupload',
        restrict: 'AE',
        scope: {},
        link: function(scope, element, attr, uploadController) {
          scope.hide = function() {
            return element.css('display', 'none');
          };
          uploadController.setSimpleWidgetScope(scope);
        }
      };
    }
  ]);

}).call(this);
