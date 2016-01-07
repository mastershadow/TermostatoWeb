var DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
var HOURS = [];
var SCHEDULING = [];
var STATUS = {};
var HISTORY = [];

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
    .then(initDashboard)
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
        $("[name='relayStatus']").bootstrapSwitch('state', STATUS.desired_relay_status);
        $("#operatingModeList").selectlist('selectByIndex', STATUS.operating_mode);
    });
}

var updateHistory = function() {
    return $.ajax({
        url : "api/temperature_history"
    }).done(function(data) {
        HISTORY = data;
        $("#morris-area-chart").empty();

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
        min: 12.0,
        max: 25.0,
        step: 0.5,
        value: 16.0,
        limitToStep: true,
        speed: 'slow'
    }).on('changed.fu.spinbox', function () {
        var id = $(this).attr("id");
        var value = $(this).spinbox("value");
        var api = "api/";
        if (id == "manualTemperatureSpinner") {
            api += "save_manualtemp";
            STATUS.manual_temperature = value;
        } else if (id == "nightTemperatureSpinner") {
            api += "save_nighttemp";
            STATUS.night_temperature = value;
        } else if (id == "weekendTemperatureSpinner") {
            api += "save_weektemp";
            STATUS.weekend_temperature = value;
        } else if (id == "dayTemperatureSpinner") {
            api += "save_daytemp";
            STATUS.day_temperature = value;
        }

        $.ajax({
            url: api,
            data : { t : value }
        });
    });

    $("#operatingModeList").on('changed.fu.selectlist', function () {
        var item = $(this).selectlist("selectedItem");
        $.ajax({
            url: "api/save_operatingmode",
            data: { mode: item.value }
        }).done(function() {
            updateStatus();
        });
        STATUS.operating_mode = item.value;
    });

    $('input[name="relayStatus"]').on('switchChange.bootstrapSwitch', function(event, state) {
        if (STATUS != null && state != STATUS.desired_relay_status) {
            $.ajax({
                url: "api/save_relaystatus",
                data: { status: state }
            }).done(function() {
                STATUS.desired_relay_status = state;
                // set manual with override
                $("#operatingModeList").selectlist('selectByIndex', 2).trigger("changed.fu.selectlist");
            });
        }
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
        }).fail(function() {
            alert("Error during saving");
        });
    });
};

var initDashboard = function() {
    $("a.reload").click(function() {
        updateStatus().then(updateHistory);
    });
};

var hideLoading = function() {
    $("#loading").hide();
    // $($(".nav li.menu")[1]).click();
};