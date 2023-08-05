angular.module('djangoCradmin.templates', ['acemarkdown/acemarkdown.tpl.html', 'bulkfileupload/fileinfolist.tpl.html', 'bulkfileupload/progress.tpl.html', 'bulkfileupload/rejectedfiles.tpl.html']);

angular.module("acemarkdown/acemarkdown.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("acemarkdown/acemarkdown.tpl.html",
    "<div ng-transclude></div>");
}]);

angular.module("bulkfileupload/fileinfolist.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bulkfileupload/fileinfolist.tpl.html",
    "<p ng-repeat=\"fileInfo in fileInfoList.files\"\n" +
    "        class=\"django-cradmin-bulkfileupload-progress-item\"\n" +
    "        ng-class=\"{\n" +
    "            'django-cradmin-bulkfileupload-progress-item-finished': fileInfoList.finished,\n" +
    "            'django-cradmin-bulkfileupload-progress-item-error django-cradmin-bulkfileupload-errorparagraph': fileInfoList.hasErrors\n" +
    "        }\">\n" +
    "    <span ng-if=\"fileInfoList.hasErrors\">\n" +
    "        <button django-cradmin-bulkfileupload-error-close-button\n" +
    "                type=\"button\"\n" +
    "                class=\"btn btn-link django-cradmin-bulkfileupload-error-closebutton\">\n" +
    "            <span class=\"fa fa-times\"></span>\n" +
    "            <span class=\"sr-only\">Close</span>\n" +
    "        </button>\n" +
    "        <span ng-repeat=\"(errorfield,errors) in fileInfoList.errors\">\n" +
    "            <span ng-repeat=\"error in errors\" class=\"django-cradmin-bulkfileupload-error\">\n" +
    "                {{ error.message }}\n" +
    "            </span>\n" +
    "        </span>\n" +
    "    </span>\n" +
    "    <span ng-if=\"!fileInfoList.hasErrors\">\n" +
    "        <button django-cradmin-bulkfileupload-remove-file-button=\"fileInfo\"\n" +
    "                ng-if=\"fileInfoList.finished\"\n" +
    "                type=\"button\"\n" +
    "                class=\"btn btn-link django-cradmin-bulkfileupload-remove-file-button\">\n" +
    "            <span ng-if=\"!fileInfo.isRemoving\"\n" +
    "                  class=\"django-cradmin-bulkfileupload-remove-file-button-isnotremoving\">\n" +
    "                <span class=\"fa fa-times\"></span>\n" +
    "                <span class=\"sr-only\">Remove</span>\n" +
    "            </span>\n" +
    "            <span ng-if=\"fileInfo.isRemoving\"\n" +
    "                  class=\"django-cradmin-bulkfileupload-remove-file-button-isremoving\">\n" +
    "                <span class=\"fa fa-spinner fa-spin\"></span>\n" +
    "                <span class=\"sr-only\">Removing ...</span>\n" +
    "            </span>\n" +
    "        </button>\n" +
    "\n" +
    "        <span class=\"django-cradmin-progressbar\">\n" +
    "            <span class=\"django-cradmin-progressbar-progress\" ng-style=\"{'width': fileInfoList.percent+'%'}\">&nbsp;</span>\n" +
    "            <span class=\"django-cradmin-progresspercent\">\n" +
    "                <span class=\"django-cradmin-progresspercent-number\">{{ fileInfoList.percent }}</span>%\n" +
    "            </span>\n" +
    "        </span>\n" +
    "        <span class=\"django-cradmin-filename\">{{fileInfo.name}}</span>\n" +
    "    </span>\n" +
    "</p>\n" +
    "");
}]);

angular.module("bulkfileupload/progress.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bulkfileupload/progress.tpl.html",
    "<div class=\"django-cradmin-bulkfileupload-progress\">\n" +
    "    <div ng-repeat=\"fileInfoList in fileInfoLists\">\n" +
    "        <div django-cradmin-bulk-file-info-list=\"fileInfoList\"\n" +
    "             class=\"django-cradmin-bulkfileupload-progress-fileinfolist\"></div>\n" +
    "    </div>\n" +
    "</div>\n" +
    "");
}]);

angular.module("bulkfileupload/rejectedfiles.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bulkfileupload/rejectedfiles.tpl.html",
    "<div class=\"django-cradmin-bulkfileupload-rejectedfiles\">\n" +
    "    <p ng-repeat=\"rejectedFile in rejectedFiles\"\n" +
    "            class=\"django-cradmin-bulkfileupload-rejectedfile django-cradmin-bulkfileupload-errorparagraph\">\n" +
    "        <button ng-click=\"closeMessage(rejectedFile)\"\n" +
    "                type=\"button\"\n" +
    "                class=\"btn btn-link django-cradmin-bulkfileupload-error-closebutton\">\n" +
    "            <span class=\"fa fa-times\"></span>\n" +
    "            <span class=\"sr-only\">Close</span>\n" +
    "        </button>\n" +
    "        <span class=\"django-cradmin-bulkfileupload-rejectedfile-filename\">{{ rejectedFile.name }}:</span>\n" +
    "        <span class=\"django-cradmin-bulkfileupload-rejectedfile-errormessage\">{{ rejectedFileErrorMessage }}</span>\n" +
    "    </p>\n" +
    "</div>\n" +
    "");
}]);
