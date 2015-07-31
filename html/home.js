



    webiopi().ready(function() {
                // Get graphs conf
                webiopi().callMacro("getConf", ["app"], updateConf);

                //var header_update = $.get("/header.js");
    });

    function updateConf(macro, args, response) {
                
        var apps = $.parseJSON(response);

        var content = $("#content");
        var header = $("#header");
        var title = $('<div id="title" class="title">');
        title.append("- eziopi -");
        header.append(title);

        // Create status link
        var link = $('<h2>').append($('<a href="/app/status">Status</a>'));
        content.append(link);

        // Create apps links
        var applist = Object.keys(apps);
        for (var i=0; i<applist.length; i++) {
                var app = applist[i];
                //alert(app);
                var id = app;
                var title = apps[app]["title"];
                var link = $('<h2>').append($('<a href="/app/'+id+'">'+title+'</a>'));
                content.append(link);
        }
    }

