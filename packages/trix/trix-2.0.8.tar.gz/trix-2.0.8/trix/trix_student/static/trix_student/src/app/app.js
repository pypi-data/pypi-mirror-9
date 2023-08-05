(function() {
  angular.module('trixStudent', ['ngCookies', 'ui.bootstrap', 'trixStudent.directives', 'trixStudent.assignments.controllers']).run([
    '$http', '$cookies', function($http, $cookies) {
      return $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
    }
  ]);

}).call(this);
