

                // Get system time
                var header = $("#header");
                var time = $('<div id="time" class="time">');
                header.append(time);
                var menu = $('<div id="menu" class="header-right">');
                var config = $('<a href="/app/config"> Config </a>');
                var debug = $('<a href="/app/debug"> debug </a>');
                var home = $('<a href="/"> Home </a>');
                //menu.append(config);
                //menu.append(debug);
                menu.append(home);
                header.append(menu);
                webiopi().callMacro("getTime", [], updateSysTime);
                // Refresh clock
                setInterval(function(){ webiopi().callMacro("getTime", [], updateSysTime);}, 60000);


    function updateSysTime(macro, args, response) {
        //alert(response);
        var timeList = $.parseJSON(response);
        $("#time").html(timeList[0]+" "+timeList[1]+"<br>");
        $("#time").append(timeList[2]);
    }

