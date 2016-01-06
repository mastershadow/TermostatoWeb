var DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
var HOURS = [];
var SCHEDULING = [];
var STATUS = null;
var HISTORY = null;

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
    $("[name='relayStatus']").bootstrapSwitch();


    $.ajax({
        url : "api/scheduling"
    })
    .done(function(data) {
        SCHEDULING = data;
    })
    .then(initSettings)
    .then(updateStatus)
    .then(updateHistory)
    .then(initScheduler)
    .then(hideLoading);
});

function padLeft(nr, n, str){
    return Array(n-String(nr).length+1).join(str||'0')+nr;
}

var updateStatus = function() {
    return $.ajax({
        url : "api/status"
    }).done(function(data) {
        STATUS = data;
        $("div.currentTemperature span").text(STATUS.current_temperature);
        $("div.desiredTemperature span").text(STATUS.scheduled_temperature);
        $("div.relayStatus").text(STATUS.relay_status ? 'ON' : 'OFF');
        $("#dayTemperatureSpinner").spinbox('value', STATUS.day_temperature);
        $("#weekendTemperatureSpinner").spinbox('value', STATUS.weekend_temperature);
        $("#nightTemperatureSpinner").spinbox('value', STATUS.night_temperature);
        $("#manualTemperatureSpinner").spinbox('value', STATUS.manual_temperature);
        $("#dayTemperatureSpinner").spinbox('value', STATUS.day_temperature);
        $("[name='relayStatus']").bootstrapSwitch('state', STATUS.relay_status);
        $("#operatingModeList").selectlist('selectByIndex', STATUS.operating_mode);
    });
}

var updateHistory = function() {
    return $.ajax({
        url : "api/temperature_history"
    }).done(function(data) {
        HISTORY = data;

        new Morris.Area({
          element: 'morris-area-chart',
          data: HISTORY,
          xkey: 'timestamp',
          ykeys: ['temperature'],
          ymax: 'auto 25',
          ymin: '12',
          hideHover : 'auto',
          labels: ['Temperature']
        });
    });
}

var initSettings = function() {
    $(".spinbox").spinbox({
        min : 12.0,
        max : 25.0,
        step : 0.5,
        value: 16.0,
        speed : 'slow'
    });
};

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
    $($(".nav li.menu")[1]).click();
}