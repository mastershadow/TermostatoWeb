var DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
var HOURS = [];

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

    initScheduler();
    $($(".nav li.menu")[1]).click();

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
    for (var k in HOURS) {
        var hour = HOURS[k];
        ul = $(document.createElement("ul"));
        s.append(ul);
        ul.append('<li class="header hour">' + hour + "</li>");
        for (var kk in DAYS) {
            var day = DAYS[kk];
            ul.append('<li class="item dotw night" data-hour="' + hour + '" data-day="' + day + '">&nbsp;</li>');
        }
    }

    var schedulerItemAction = function(e) {
        if (e.buttons == 1) {
            var item = $(this);
            // TODO get current status
            // TODO set to new status if needed
            item.toggleClass("night").toggleClass("day");
        }
    };
    // mouse events
    $("li.item", s).mouseenter(schedulerItemAction);
    $("li.item", s).mousedown(schedulerItemAction);

}