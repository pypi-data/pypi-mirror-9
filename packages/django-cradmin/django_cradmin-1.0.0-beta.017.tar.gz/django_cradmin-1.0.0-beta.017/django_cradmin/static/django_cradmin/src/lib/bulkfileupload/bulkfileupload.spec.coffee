angular.module('djangoCradmin.detectizrMockDesktop', [])
.factory 'cradminDetectize', ->
  return {
    device: {
      type: 'desktop'
    }
  }

angular.module('djangoCradmin.detectizrMockMobile', [])
.factory 'cradminDetectize', ->
  return {
    device: {
      type: 'mobile'
    }
  }


describe 'djangoCradminBulkfileuploadAdvanced', ->
  $compile = null
  $rootScope = null
  beforeEach(module('djangoCradmin.bulkfileupload', 'djangoCradmin.detectizrMockDesktop'))

  # Store references to $rootScope and $compile
  # so they are available to all tests in this describe block
  beforeEach inject((_$compile_, _$rootScope_) ->
    # The injector unwraps the underscores (_) from around the parameter names when matching
    $compile = _$compile_
    $rootScope = _$rootScope_
  )

  it 'should hide simple widget', ->
    scope = {}
    html = """
      <form django-cradmin-bulkfileupload-form>
        <div django-cradmin-bulkfileupload="/file_upload_api_mock">
          <div django-cradmin-bulkfileupload-advanced-widget id="advanced"></div>
          <div django-cradmin-bulkfileupload-simple-widget id="simple"></div>
        </div>
      </form>
    """
    element = $compile(html)($rootScope)
    $rootScope.$digest()
    expect(element.find('#simple').css('display')).toBe('none')
    expect(element.find('#advanced').css('display')).toBe('')


describe 'djangoCradminBulkfileuploadMobile', ->
  $compile = null
  $rootScope = null
  beforeEach(module('djangoCradmin.bulkfileupload', 'djangoCradmin.detectizrMockMobile'))

  # Store references to $rootScope and $compile
  # so they are available to all tests in this describe block
  beforeEach inject((_$compile_, _$rootScope_) ->
    # The injector unwraps the underscores (_) from around the parameter names when matching
    $compile = _$compile_
    $rootScope = _$rootScope_
  )

  it 'should hide advanced widget', ->
    scope = {}
    html = """
      <form django-cradmin-bulkfileupload-form>
        <div django-cradmin-bulkfileupload="/file_upload_api_mock">
          <div django-cradmin-bulkfileupload-advanced-widget id="advanced"></div>
          <div django-cradmin-bulkfileupload-simple-widget id="simple"></div>
        </div>
      </form>
    """
    element = $compile(html)($rootScope)
    $rootScope.$digest()
    expect(element.find('#simple').css('display')).toBe('')
    expect(element.find('#advanced').css('display')).toBe('none')


describe 'djangoCradminBulkfileuploadInProgressOrFinished', ->
  $compile = null
  $rootScope = null
  formElement = null
  inProgressOrFinishedElement = null
  inProgressOrFinishedScope = null

  beforeEach(module(
    'djangoCradmin.bulkfileupload',
    'djangoCradmin.templates',
    'djangoCradmin.detectizrMockDesktop'
  ))

  beforeEach inject((_$compile_, _$rootScope_) ->
    $compile = _$compile_
    $rootScope = _$rootScope_
    html = """
      <form django-cradmin-bulkfileupload-form>
        <div django-cradmin-bulkfileupload="/file_upload_api_mock">
          <div django-cradmin-bulkfileupload-progress id="progress"></div>
        </div>
      </form>
    """

    formElement = $compile(html)($rootScope)
    $rootScope.$digest()
    inProgressOrFinishedElement = formElement.find('#progress')
    inProgressOrFinishedScope = inProgressOrFinishedElement.isolateScope()
  )

  getProgressPercents = ->
    progressPercents = []
    elements = inProgressOrFinishedElement.find('.django-cradmin-progresspercent-number')
    for domelement in elements
      percent = angular.element(domelement).text().trim()
      progressPercents.push(percent)
    return progressPercents

  getProgressFilenames = ->
    filenames = []
    elements = inProgressOrFinishedElement.find('.django-cradmin-filename')
    for domelement in elements
      filename = angular.element(domelement).text().trim()
      filenames.push(filename)
    return filenames

  it 'should re-render when adding FileInfoList', ->
    expect(inProgressOrFinishedElement.find(
      '.django-cradmin-bulkfileupload-progress-item').length).toBe(0)
    inProgressOrFinishedScope.fileInfoLists.push({
      percent: 0
      files: [{name: 'test.txt'}]
    })
    inProgressOrFinishedScope.$apply()
    expect(inProgressOrFinishedElement.find(
      '.django-cradmin-bulkfileupload-progress-item').length).toBe(1)

  it 'should re-render when changing percent', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 0
      files: [{name: 'test.txt'}]
    }]
    inProgressOrFinishedScope.$apply()
    expect(getProgressPercents()[0]).toBe('0')

    inProgressOrFinishedScope.fileInfoLists[0].percent = '20'
    inProgressOrFinishedScope.$apply()
    expect(getProgressPercents()[0]).toBe('20')

  it 'should render files when one file in each item', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 0
      files: [{name: 'test1.txt'}]
    }, {
      percent: 0
      files: [{name: 'test2.txt'}]
    }]
    inProgressOrFinishedScope.$apply()
    expect(getProgressFilenames()[0]).toBe('test1.txt')
    expect(getProgressFilenames()[1]).toBe('test2.txt')
    expect(inProgressOrFinishedElement.find(
      '.django-cradmin-bulkfileupload-progress-fileinfolist').length).toBe(2)

  it 'should render files when multiple files in each item', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 0
      files: [{name: 'test1.txt'}, {name: 'test2.txt'}]
    }, {
      percent: 0
      files: [{name: 'test3.txt'}, {name: 'test4.txt'}]
    }]
    inProgressOrFinishedScope.$apply()
    expect(getProgressFilenames()[0]).toBe('test1.txt')
    expect(getProgressFilenames()[1]).toBe('test2.txt')
    expect(getProgressFilenames()[2]).toBe('test3.txt')
    expect(getProgressFilenames()[3]).toBe('test4.txt')
    expect(inProgressOrFinishedElement.find(
      '.django-cradmin-bulkfileupload-progress-fileinfolist').length).toBe(2)

  it 'should add finished class when finished', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      finished: true
      files: [{name: 'test1.txt'}]
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.hasClass('django-cradmin-bulkfileupload-progress-item-finished')).toBe(true)

  it 'should add error message on error', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      files: [{name: 'test1.txt'}]
      hasErrors: true
      errors: {
        file: [{
          message: 'File is too big'
        }]
      }
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.find('.django-cradmin-bulkfileupload-error').length).toBe(1)
    expect(firstItem.find('.django-cradmin-bulkfileupload-error').text().trim()).toBe('File is too big')

  it 'should add error class on error', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      files: [{name: 'test1.txt'}]
      hasErrors: true
      errors: {}
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.hasClass('django-cradmin-bulkfileupload-progress-item-error')).toBe(true)

  it 'should show delete button when finished', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      finished: true
      files: [{name: 'test1.txt'}]
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button').length).toBe(1)

  it 'should not show delete button when not finished', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      finished: false
      files: [{name: 'test1.txt'}]
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button').length).toBe(0)

  it 'should not show delete button when not successful', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      finished: true
      files: [{name: 'test1.txt'}]
      hasErrors: true
      errors: {}
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button').length).toBe(0)

  it 'should show isRemoving message when removing', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      finished: true
      files: [{name: 'test1.txt', isRemoving: true}]
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isremoving').length).toBe(1)
    expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isnotremoving').length).toBe(0)

  it 'should not show isRemoving message when not removing', ->
    inProgressOrFinishedScope.fileInfoLists = [{
      percent: 100
      finished: true
      files: [{name: 'test1.txt'}]
    }]
    inProgressOrFinishedScope.$apply()
    firstItem = inProgressOrFinishedElement.find('.django-cradmin-bulkfileupload-progress-item')
    expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isremoving').length).toBe(0)
    expect(firstItem.find('.django-cradmin-bulkfileupload-remove-file-button-isnotremoving').length).toBe(1)
