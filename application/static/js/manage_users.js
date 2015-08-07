/* load drag-and-drop directives -- credit: http://logicbomb.github.io/ng-directives/script/lvl-drag-drop.js */
angular
.module('lvl.services',[])
.factory('uuid', function() {
    var svc = {
        new: function() {
            function _p8(s) {
                var p = (Math.random().toString(16)+"000000000").substr(2,8);
                return s ? "-" + p.substr(0,4) + "-" + p.substr(4,4) : p ;
            }
            return _p8() + _p8(true) + _p8(true) + _p8();
        },
         
        empty: function() {
          return '00000000-0000-0000-0000-000000000000';
        }
    };
     
    return svc;
});

var module = angular.module("lvl.directives.dragdrop", ['lvl.services']);

module.directive('lvlDraggable', ['$rootScope', 'uuid', function($rootScope, uuid) {
  return {
    restrict: 'A',
    link: function(scope, el, attrs, controller) {
      angular.element(el).attr("draggable", "true");
      
      var id = angular.element(el).attr("id");
      
      if (!id) {
        id = uuid.new()
        angular.element(el).attr("id", id);
      }
      
      el.bind("dragstart", function(e) {
        e.dataTransfer.setData('text', id);
        $rootScope.$emit("LVL-DRAG-START");
      });
      
      el.bind("dragend", function(e) {
        $rootScope.$emit("LVL-DRAG-END");
      });
    }
  }
}]);
module.directive('lvlDropTarget', ['$rootScope', 'uuid', function($rootScope, uuid) {
  return {
    restrict: 'A',
    scope: {
      onDrop: '&'
    },
    link: function(scope, el, attrs, controller) {
      
      var id = angular.element(el).attr("id");
      
      if (!id) {
        id = uuid.new();
        angular.element(el).attr("id", id);
      }
      
      el.bind("dragover", function(e) {
        if (e.preventDefault) {
          e.preventDefault();
        }
        
        e.dataTransfer.dropEffect = 'move';
        return false;
      });
      
      el.bind("dragenter", function(e) {
        // this / e.target is the current hover target.
        angular.element(e.target).addClass('lvl-over');
      });
      
      el.bind("dragleave", function(e) {
        angular.element(e.target).removeClass('lvl-over');  // this / e.target is previous target element.
      });
      
      el.bind("drop", function(e) {
        if (e.preventDefault) {
          e.preventDefault();
        }
        
        if (e.stopPropagation) {
          e.stopPropagation();
        }
        var data = e.dataTransfer.getData("text");
        var dest = document.getElementById(id);
        var src = document.getElementById(data);
        
        scope.onDrop({dragEl: src, dropEl: dest});
        $rootScope.$emit("LVL-DRAG-END");
      });
      
      $rootScope.$on("LVL-DRAG-START", function() {
        var el = document.getElementById(id);
        angular.element(el).addClass("lvl-target");
      });
      
      $rootScope.$on("LVL-DRAG-END", function() {
        var el = document.getElementById(id);
        angular.element(el).removeClass("lvl-target");
        
        var els = document.getElementsByClassName("lvl-over");
        for (var e in els) {
          angular.element(els[e]).removeClass("lvl-over");
        }
      });
    }
  }
}]);
/*end directives*/

var userData = [
  {id:1,firstName:'Mary',lastName:'Goodman',role:'manager',approved:true,points:34},
  {id:2,firstName:'Mark',lastName:'Wilson',role:'developer',approved:true,points:4},
  {id:3,firstName:'Alex',lastName:'Davies',role:'admin',approved:true,points:56},
  {id:4,firstName:'Bob',lastName:'Banks',role:'manager',approved:false,points:14},
  {id:5,firstName:'David',lastName:'Stevens',role:'developer',approved:false,points:100},
  {id:6,firstName:'Jason',lastName:'Durham',role:'developer',approved:false,points:0},
  {id:7,firstName:'Jeff',lastName:'Marks',role:'manager',approved:true,points:8},
  {id:8,firstName:'Betty',lastName:'Abercrombie',role:'manager',approved:true,points:18},
  {id:9,firstName:'Krista',lastName:'Michaelson',role:'developer',approved:true,points:10},
  {id:11,firstName:'Devin',lastName:'Sumner',role:'manager',approved:false,points:3},
  {id:12,firstName:'Navid',lastName:'Palit',role:'manager',approved:true,points:57},
  {id:13,firstName:'Bhat',lastName:'Phuart',role:'developer',approved:false,points:314},
  {id:14,firstName:'Nuper',lastName:'Galzona',role:'admin',approved:true,points:94}
];

function ctrlDualList($scope) {
 
  // init
  $scope.selectedA = [];
  $scope.selectedB = [];
   
  $scope.listA = userData.slice(0,5);
  $scope.listB = userData.slice(6,10);
  $scope.items = userData;
  
  $scope.checkedA = false;
  $scope.checkedB = false;
  
  function arrayObjectIndexOf(myArray, searchTerm, property) {
      for(var i = 0, len = myArray.length; i < len; i++) {
          if (myArray[i][property] === searchTerm) return i;
      }
      return -1;
  }
  
  $scope.aToB = function() {
    for (i in $scope.selectedA) {
      var moveId = arrayObjectIndexOf($scope.items, $scope.selectedA[i], "id"); 
      $scope.listB.push($scope.items[moveId]);
      var delId = arrayObjectIndexOf($scope.listA, $scope.selectedA[i], "id"); 
      $scope.listA.splice(delId,1);
    }
    reset();
  };
  
  $scope.bToA = function() {
    for (i in $scope.selectedB) {
      var moveId = arrayObjectIndexOf($scope.items, $scope.selectedB[i], "id"); 
      $scope.listA.push($scope.items[moveId]);
      var delId = arrayObjectIndexOf($scope.listB, $scope.selectedB[i], "id"); 
      $scope.listB.splice(delId,1);
    }
    reset();
  };
  
  function reset(){
    $scope.selectedA=[];
    $scope.selectedB=[];
    $scope.toggle=0;
  }
  
  $scope.toggleA = function() {
    
    if ($scope.selectedA.length>0) {
      $scope.selectedA=[];
    }
    else {
      for (i in $scope.listA) {
        $scope.selectedA.push($scope.listA[i].id);
      }
    }
  }
  
  $scope.toggleB = function() {
    
    if ($scope.selectedB.length>0) {
      $scope.selectedB=[];
    }
    else {
      for (i in $scope.listB) {
        $scope.selectedB.push($scope.listB[i].id);
      }
    }
  }
 
  $scope.drop = function(dragEl, dropEl, direction) {
    
    var drag = angular.element(dragEl);
    var drop = angular.element(dropEl);
    var id = drag.attr("data-id");
    var el = document.getElementById(id);
    
    if(!angular.element(el).attr("checked")){
      angular.element(el).triggerHandler('click');
    }
    
    direction();
    $scope.$digest();
  };
  
};
  
angular
  .module('myApp', ['lvl.directives.dragdrop']) 
  .controller('ctrlDualList', ['$scope', ctrlDualList]);
  
$(document).ready(function() {
  jQuery.event.props.push('dataTransfer'); //prevent conflict with drag-drop
});