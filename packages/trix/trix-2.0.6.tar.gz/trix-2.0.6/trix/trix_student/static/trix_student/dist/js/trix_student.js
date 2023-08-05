(function() {
  angular.module('trixStudent', ['ngCookies', 'ui.bootstrap', 'trixStudent.directives', 'trixStudent.assignments.controllers']).run([
    '$http', '$cookies', function($http, $cookies) {
      return $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
    }
  ]);

}).call(this);

(function() {
  angular.module('trixStudent.assignments.controllers', []).controller('AddTagCtrl', [
    '$scope', '$window', function($scope, $window) {
      $scope.tagToAdd = '';
      $scope.addTag = function() {
        var currentUrl, tags;
        currentUrl = new Url();
        tags = currentUrl.query.tags;
        if ((tags != null) && tags !== '') {
          tags = "" + tags + "," + $scope.tagToAdd;
        } else {
          tags = $scope.tagToAdd;
        }
        currentUrl.query.tags = tags;
        delete currentUrl.query['page'];
        return $window.location.href = currentUrl.toString();
      };
    }
  ]).controller('RemoveTagCtrl', [
    '$scope', '$window', function($scope, $window) {
      return $scope.removeTag = function(tagToRemove) {
        var currentUrl, index, tags, tagsArray;
        currentUrl = new Url();
        tags = currentUrl.query.tags;
        tagsArray = tags.split(',');
        index = tagsArray.indexOf(tagToRemove);
        tagsArray.splice(index, 1);
        tags = tagsArray.join(',');
        currentUrl.query.tags = tags;
        delete currentUrl.query['page'];
        return $window.location.href = currentUrl.toString();
      };
    }
  ]).controller('SolutionCtrl', [
    '$scope', function($scope) {
      return $scope.isVisible = false;
    }
  ]).controller('AssignmentCtrl', [
    '$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {
      $scope.howsolved = null;
      $scope.saving = false;
      $scope.buttonClass = 'btn-default';
      $scope.boxClass = '';
      $scope.$watch('howsolved', function(newValue) {
        if (newValue === 'bymyself') {
          $scope.buttonClass = 'btn-success';
          $scope.boxClass = 'trix-assignment-solvedbymyself';
        } else if (newValue === 'withhelp') {
          $scope.buttonClass = 'btn-warning';
          $scope.boxClass = 'trix-assignment-solvedwithhelp';
        } else {
          $scope.buttonClass = 'btn-default';
          $scope.boxClass = 'trix-assignment-notsolved';
        }
        $rootScope.$emit('assignments.progressChanged');
      });
      $scope._getApiUrl = function() {
        return "/assignment/howsolved/" + $scope.assignment_id;
      };
      $scope._showError = function(message) {
        $scope.saving = false;
        return alert(message);
      };
      $scope._updateHowSolved = function(howsolved) {
        var data;
        $scope.saving = true;
        data = {
          howsolved: howsolved
        };
        return $http.post($scope._getApiUrl(), data).success(function(data) {
          $scope.saving = false;
          return $scope.howsolved = data.howsolved;
        }).error(function(data) {
          return $scope._showError('An error occurred!');
        });
      };
      $scope.solvedOnMyOwn = function() {
        return $scope._updateHowSolved('bymyself');
      };
      $scope.solvedWithHelp = function() {
        return $scope._updateHowSolved('withhelp');
      };
      return $scope.notSolved = function() {
        $scope.saving = true;
        return $http["delete"]($scope._getApiUrl()).success(function(data) {
          $scope.saving = false;
          return $scope.howsolved = null;
        }).error(function(data, status) {
          if (status === 404) {
            $scope.saving = false;
            return $scope.howsolved = null;
          } else {
            return $scope._showError('An error occurred!');
          }
        });
      };
    }
  ]).controller('AssignmentListProgressController', [
    '$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {
      var apiUrl, unbindProgressChanged;
      $scope.loading = true;
      apiUrl = new Url();
      apiUrl.query.progressjson = '1';
      $scope._loadProgress = function() {
        $scope.loading = true;
        return $http.get(apiUrl.toString()).success(function(data) {
          $scope.loading = false;
          $scope.solvedPercentage = data.percent;
          if ($scope.solvedPercentage > 1 && $scope.solvedPercentage < 20) {
            return $scope.progressBarClass = 'progress-bar-danger';
          } else if ($scope.solvedPercentage < 45) {
            return $scope.progressBarClass = 'progress-bar-warning';
          } else if ($scope.solvedPercentage === 100) {
            return $scope.progressBarClass = 'progress-bar-success';
          } else {
            return $scope.progressBarClass = '';
          }
        }).error(function(data) {
          return console.error('Failed to load progress:', data);
        });
      };
      unbindProgressChanged = $rootScope.$on('assignments.progressChanged', function() {
        return $scope._loadProgress();
      });
      return $scope.$on('$destroy', unbindProgressChanged);
    }
  ]);

}).call(this);

(function() {
  angular.module('trixStudent.directives', []).directive('trixAriaChecked', function() {
    return {
      restrict: 'A',
      scope: {
        'checked': '=trixAriaChecked'
      },
      controller: function($scope) {},
      link: function(scope, element, attrs) {
        var updateAriaChecked;
        updateAriaChecked = function() {
          if (scope.checked) {
            return element.attr('aria-checked', 'true');
          } else {
            return element.attr('aria-checked', 'false');
          }
        };
        updateAriaChecked();
        scope.$watch(attrs.trixAriaChecked, function(newValue, oldValue) {
          return updateAriaChecked();
        });
      }
    };
  });

}).call(this);
