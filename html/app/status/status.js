



    webiopi().ready(function() {
                // Get graphs conf
                webiopi().callMacro("getConf", ["graphs"], updateConf);

                var header_update = $.get("/header.js");
    });

    function updateConf(macro, args, response) {
        // Avoid webiopi's jquery conflict with javascriptRRD's
        var $j = jQuery.noConflict();
                
        var graphs = $j.parseJSON(response);
        var content = $j("#content");
        var header = $j("#header");
        var title = $j('<div id="title" class="title">');
        title.append("- Status -");
        header.append(title);

        var rrdflot_defaults={ "graph_height": "15em", 
                                "graph_width": "100%", 
                                "graph_only": false
                            };

                // Create graphs boxes
                for (var i=0; i<graphs.length; i++) {
                        var id = graphs[i]["id"];
                        var file = "status/" + graphs[i]["rrd"];
                        var title = graphs[i]["title"];

                        var box = $j('<div class="graph_box" align="center">');
                        box.append(title);

                        // Create RRDFlot graphs
                        var graph_opts = graphs[i]["graph_opts"];

                        var ds_graph_opts = {}
                        var sources = graphs[i]["sources"];
                        for (var j=0; j<sources.length; j++) {
                            var ds = sources[j]["ds"];
                            var ds_opts = sources[j]["ds_opts"];
                            ds_graph_opts[ds] = ds_opts;
                        }
                        var graph = $j('<div class="graph" id=' + id + '>');

                        simple = new rrdFlotAsync(id,file,null,graph_opts,ds_graph_opts,rrdflot_defaults);

                        graph.append(id);
                        box.append(graph);
                        content.append(box);
                }
    }
