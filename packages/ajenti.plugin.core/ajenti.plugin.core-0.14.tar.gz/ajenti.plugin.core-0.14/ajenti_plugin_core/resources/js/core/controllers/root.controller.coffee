angular.module('core').controller 'CoreRootController', ($scope, $rootScope, $location, $cookieStore, $q, identity, urlPrefix, ajentiPlugins, ajentiVersion) ->
    $rootScope.identity = identity
    $rootScope.$location = $location
    $rootScope.location = location
    $rootScope.urlPrefix = urlPrefix
    $rootScope.ajentiVersion = ajentiVersion
    $rootScope.ajentiPlugins = ajentiPlugins

    console.group('Welcome')
    console.log('Ajenti', ajentiVersion)
    if urlPrefix
        console.log('URL prefix', urlPrefix)
    console.log('Plugins', ajentiPlugins)
    console.groupEnd()

    $scope.navigationPresent = $location.path().indexOf('/view/login') != 0

    $scope.showSidebar = $cookieStore.get('showSidebar') ? true
    $scope.toggleNavigation = (state) ->
        if angular.isDefined state
            $scope.showSidebar = state
        else
            $scope.showSidebar = !$scope.showSidebar
        $cookieStore.put('showSidebar', $scope.showSidebar)
        $scope.$broadcast 'navigation:toggle'

    $scope.showOverlaySidebar = false
    $scope.toggleOverlayNavigation = (state) ->
        if angular.isDefined state
            $scope.showOverlaySidebar = state
        else
            $scope.showOverlaySidebar = !$scope.showOverlaySidebar
        $scope.$broadcast 'navigation:toggle'

    $scope.$on '$routeChangeSuccess', () ->
        $scope.toggleOverlayNavigation(false)

    $rootScope.appReady = true
    identity.init()
    identity.promise.then () ->
        console.log 'Ready!'
    .catch () ->
        console.error 'Failed'

    $rootScope.theme = 'deeporange'

    setTimeout () ->
        $(window).resize () ->
            $scope.$apply () ->
                $rootScope.$broadcast 'window:resize'
