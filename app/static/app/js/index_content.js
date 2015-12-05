/**
 * Created by JeOam on 1/12/15.
 */

"use strict";


var list = document.getElementById("main-sortable");
Sortable.create(list, {
    animation: 150,
    forceFallback: true,
});

var groups = document.getElementById("main-sortable").getElementsByClassName('item-sortable');
[].forEach.call(groups, function (el){
    Sortable.create(el, {
        group: 'groups',
        animation: 150,
        forceFallback: true,
    });
});

var lockBtn = $("#lock-btn")
lockBtn.on("click", function(event){
  if (lockBtn.hasClass("fa-lock")) {
      lockBtn.removeClass("fa-lock");
      $(".title-sortable").addClass("cursor-move");
      $(".item-sortable>li").addClass("cursor-move");
      lockBtn.addClass("fa-unlock");
  } else {
      lockBtn.removeClass("fa-unlock");
      $(".title-sortable").removeClass("cursor-move");
      $(".item-sortable>li").removeClass("cursor-move");
      lockBtn.addClass("fa-lock");
  }
});
