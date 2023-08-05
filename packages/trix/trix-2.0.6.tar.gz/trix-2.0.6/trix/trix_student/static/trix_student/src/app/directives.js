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
