var DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
var HOURS = [];
var SCHEDULING = [];

$(document).ready(function() {

    $(".nav li.menu").click(function() {
        var item = $(this);
        var what = item.attr("data-menu");
        $(".nav li.menu").removeClass("active");
        item.addClass("active");
        $("#page-wrapper > div").addClass("hidden");
        $("#" + what).removeClass("hidden");
    });

    $("a.logout").click(function() {
        return confirm("Are you sure?");
    });

    $.ajax({
        url : "api/scheduling"
    }).done(function(data) {
        SCHEDULING = data;
    }).then(function() {
        initScheduler();
    })

    new Morris.Area({
      element: 'morris-area-chart',
      data: [
        { time: '2016-01-03 10:00', value: 20.1 },
        { time: '2016-01-03 10:15', value: 20.2 },
        { time: '2016-01-03 10:30', value: 20.1 },
        { time: '2016-01-03 10:45', value: 20.3 },
        { time: '2016-01-03 11:00', value: 20.4 },
        { time: '2016-01-03 11:15', value: 19.8 },
        { time: '2016-01-03 11:30', value: 19.8 }
      ],
      xkey: 'time',
      ykeys: ['value'],
      ymax: 'auto 21',
      ymin: '12',
      hideHover : 'auto',
      labels: ['Temperature']
    });

    $("[name='relayStatus']").bootstrapSwitch();
    $($(".nav li.menu")[1]).click();
    hideLoading();
});

function padLeft(nr, n, str){
    return Array(n-String(nr).length+1).join(str||'0')+nr;
}

var initScheduler = function() {
    // GENERATE HOURS
    for (var h = 0; h < 24; h++) {
        for (var m = 0; m < 60; m += 30) {
            var hm = padLeft(h, 2) + ":" + padLeft(m, 2);
            HOURS.push(hm);
        }
    }

    var s = $("#scheduler");
    var ul = $(document.createElement("ul"));
    s.append(ul);
    ul.append('<li class="header hour">&nbsp;</li>');
    for (var k in DAYS) {
        ul.append('<li class="header dotw">' + DAYS[k] + "</li>");
    }
    for (var hourIdx in HOURS) {
        var hour = HOURS[hourIdx];
        ul = $(document.createElement("ul"));
        s.append(ul);
        ul.append('<li class="header hour">' + hour + "</li>");
        for (var dayIdx in DAYS) {
            var day = DAYS[dayIdx];
            var status = SCHEDULING[dayIdx][hourIdx];
            if (status == 0) {
                status = "night";
            } else if (status == 1) {
                status = "day";
            } else if (status == 2) {
                status = "week";
            }
            ul.append('<li class="item dotw ' + status + '" data-hour="' + hourIdx + '" data-day="' + dayIdx + '">&nbsp;</li>');
        }
    }


    var newItemStatus = null;
    var schedulerItemDown = function(e) {
        if (e.buttons == 1) {
            var item = $(this);
            var hourIdx = item.attr("data-hour");
            var dayIdx = item.attr("data-day");
            // get current status
            var status = SCHEDULING[dayIdx][hourIdx];
            if (status == 0) {
                newItemStatus = 1;
                item.removeClass("night").removeClass("week").addClass("day");
            } else if (status == 1) {
                newItemStatus = 2;
                item.removeClass("day").removeClass("night").addClass("week");
            } else if (status == 2) {
                newItemStatus = 0;
                item.removeClass("day").removeClass("week").addClass("night");
            }
            SCHEDULING[dayIdx][hourIdx] = newItemStatus;
        }
    };
    var schedulerItemEnter = function(e) {
        if (e.buttons == 1 && newItemStatus != null) {
            var item = $(this);
            var hourIdx = item.attr("data-hour");
            var dayIdx = item.attr("data-day");
            if (newItemStatus == 1) {
                item.removeClass("night").removeClass("week").addClass("day");
            } else if (newItemStatus == 2) {
                item.removeClass("day").removeClass("night").addClass("week");
            } else if (newItemStatus == 0) {
                item.removeClass("day").removeClass("week").addClass("night");
            }
            SCHEDULING[dayIdx][hourIdx] = newItemStatus;
        }
    };
    // mouse events
    $("li.item", s).mouseenter(schedulerItemEnter);
    $("li.item", s).mousedown(schedulerItemDown);
    $("body").mouseup(function() {
        newItemStatus = null;
    });
    $(".save-scheduling").click(function() {
        var data = JSON.stringify(SCHEDULING);
        $.ajax({
            url: "api/save_scheduling",
            data : data,
            type: "POST",
            contentType: 'application/json',
            processData: false,
            dataType: 'json',
            success: function(response) {
                console.log(response);
            }
        });
    });
}

var hideLoading = function() {
    $("#loading").hide();
}