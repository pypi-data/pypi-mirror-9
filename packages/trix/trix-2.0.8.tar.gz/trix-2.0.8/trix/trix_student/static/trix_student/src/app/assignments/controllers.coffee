angular.module('trixStudent.assignments.controllers', [])

.controller('AddTagCtrl', [
  '$scope', '$window',
  ($scope, $window) ->
    $scope.tagToAdd = ''
    $scope.addTag = ->
      currentUrl = new Url()
      tags = currentUrl.query.tags
      if tags? and tags != ''
        tags = "#{tags},#{$scope.tagToAdd}"
      else
        tags = $scope.tagToAdd
      currentUrl.query.tags = tags
      delete currentUrl.query['page']
      $window.location.href = currentUrl.toString()
    return
])

.controller('RemoveTagCtrl', [
  '$scope', '$window',
  ($scope, $window) ->
    $scope.removeTag = (tagToRemove) ->
      currentUrl = new Url()
      tags = currentUrl.query.tags
      tagsArray = tags.split(',')
      index = tagsArray.indexOf(tagToRemove)
      tagsArray.splice(index, 1)
      tags = tagsArray.join(',')
      currentUrl.query.tags = tags
      delete currentUrl.query['page']
      $window.location.href = currentUrl.toString()
])

.controller('SolutionCtrl', [
  '$scope',
  ($scope) ->
    $scope.isVisible = false
])

.controller('AssignmentCtrl', [
  '$scope', '$http', '$rootScope',
  ($scope, $http, $rootScope) ->
    $scope.howsolved = null
    $scope.saving = false
    $scope.buttonClass = 'btn-default'
    $scope.boxClass = ''

    $scope.$watch 'howsolved', (newValue) ->
      if newValue == 'bymyself'
        $scope.buttonClass = 'btn-success'
        $scope.boxClass = 'trix-assignment-solvedbymyself'
      else if newValue == 'withhelp'
        $scope.buttonClass = 'btn-warning'
        $scope.boxClass = 'trix-assignment-solvedwithhelp'
      else
        $scope.buttonClass = 'btn-default'
        $scope.boxClass = 'trix-assignment-notsolved'

      # Tell AssignmentListProgressController to reload
      $rootScope.$emit('assignments.progressChanged')
      return

    $scope._getApiUrl = ->
      return "/assignment/howsolved/#{$scope.assignment_id}"

    $scope._showError = (message) ->
      # TODO: Use bootstrap modal and a scope variable
      $scope.saving = false
      alert(message)

    $scope._updateHowSolved = (howsolved) ->
      $scope.saving = true
      data = {
        howsolved: howsolved
      }
      $http.post($scope._getApiUrl(), data)
        .success (data) ->
          $scope.saving = false
          $scope.howsolved = data.howsolved
        .error (data) ->
          $scope._showError('An error occurred!')

    $scope.solvedOnMyOwn = ->
      $scope._updateHowSolved('bymyself')
      # $scope.howsolved = 'bymyself'

    $scope.solvedWithHelp = ->
      $scope._updateHowSolved('withhelp')
      # $scope.howsolved = 'withhelp'

    $scope.notSolved = ->
      $scope.saving = true
      $http.delete($scope._getApiUrl())
        .success (data) ->
          $scope.saving = false
          $scope.howsolved = null
        .error (data, status) ->
          if status == 404  # Handle 404 just like 200
            $scope.saving = false
            $scope.howsolved = null
          else
            $scope._showError('An error occurred!')
])

.controller('AssignmentListProgressController', [
  '$scope', '$http', '$rootScope',
  ($scope, $http, $rootScope) ->
    $scope.loading = true
    apiUrl = new Url()
    apiUrl.query.progressjson = '1'

    $scope._loadProgress = ->
      $scope.loading = true
      $http.get(apiUrl.toString())
        .success (data) ->
          $scope.loading = false
          $scope.solvedPercentage = data.percent
          if $scope.solvedPercentage > 1 and $scope.solvedPercentage < 20
            $scope.progressBarClass = 'progress-bar-danger'
          else if $scope.solvedPercentage < 45
            $scope.progressBarClass = 'progress-bar-warning'
          else if $scope.solvedPercentage == 100
            $scope.progressBarClass = 'progress-bar-success'
          else
            $scope.progressBarClass = ''
        .error (data) ->
          console.error('Failed to load progress:', data)
    # $scope._loadProgress()

    unbindProgressChanged = $rootScope.$on 'assignments.progressChanged', ->
      $scope._loadProgress()
    $scope.$on('$destroy', unbindProgressChanged)
])
