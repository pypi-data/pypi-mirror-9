angular.module('core').service 'identity', ($http, $location, $window, $timeout, $q, urlPrefix) ->
    @init = () ->
        q = $q.defer()
        @promise = q.promise
        $http.get('/api/core/identity').success (data) =>
            @user = data.identity.user
            @effective = data.identity.effective
            @machine = data.machine
            @color = data.color
            @isSuperuser = @user == 'root'
            q.resolve()
        .error () ->
            q.reject()

    @init()

    @auth = (username, password, mode) ->
        q = $q.defer()

        data = {
            username: username
            password: password
            mode: mode
        }
        $http.post('/api/core/auth', data).success (data) ->
            if data.success
                q.resolve(data.username)
            else
                q.reject(data.error)
        .error () ->
            q.reject()

        return q.promise

    @personaAuth = (assertion, audience) ->
        q = $q.defer()

        data = {
            assertion: assertion
            audience: audience
            mode: 'persona'
        }
        $http.post('/api/core/auth', data).success (data) ->
            if data.success
                q.resolve(data.username)
            else
                q.reject(data.error)
        .error () ->
            q.reject()

        return q.promise

    @login = () ->
        $window.location.assign("#{urlPrefix}/view/login/normal/#{$location.path()}")

    @elevate = () ->
        q = $q.defer()
        $http.get('/api/core/logout')
        $timeout () =>
            q.resolve()
            $window.location.assign("#{urlPrefix}/view/login/sudo:#{@user}/#{$location.path()}")
        , 1000
        return q.promise

    @logout = () ->
        q = $q.defer()
        $http.get('/api/core/logout')
        $timeout () ->
            q.resolve()
            $window.location.assign("#{urlPrefix}/view/login/normal/#{$location.path()}")
        , 1000
        return q.promise

    return this
