// Dependencies:
//   miner/js/plot-util.js
//   d3.js

function mouseover(d) {
    var focus = d3.select("g.focus");
    translate_value = "translate(" + mouseover.conf.xscale(d.x);
    // var text_anchor = mouseover.conf.xscale(d.x) > d3.mean(mouseover.conf.xscale.range()) ? "end" : "start";
    if (mouseover.conf.stacked) {
      translate_value = translate_value + "," + mouseover.conf.yscale(d3.max([d.y0, d.y])) + ")";
      }
    else {
      translate_value = translate_value + "," + mouseover.conf.yscale(d.y) + ")";
      }
    focus.attr("transform", translate_value);
    console.log('translate = ' + translate_value + '   stacked = ' + mouseover.conf.stacked);
    console.log(mouseover.conf.yscale);
    var tt = d.heading + ": " + (d.y).toFixed(1) + "%";
    var text = focus.select("text").text(tt).node();
    var SVGRect = text.getBBox();
    focus.select("rect").attr("x", SVGRect.x).attr("y", SVGRect.y).attr("width", SVGRect.width).attr("height", SVGRect.height);
    console.log(d);
    console.log(mouseover.conf.yscale(d.y));
    console.log(d3.mean(mouseover.conf.yscale.range()));
    console.log(d3.mean(mouseover.conf.yscale.domain()));
}
mouseover.conf = null;


function mouseout(d) {
  var focus = d3.select("g.focus");
  focus.select("text").text("");
  focus.select("rect").attr("width", 0).attr("height", 0);
    
  // FIXME: doesn't work
  // selector = ".row-"+d.row + ".col-"+d.col;
  // console.log('mouse out selector: ' + selector);
  // console.log(d);
  // d3.select().classed('hover', false);
}


function bar_plot(d3data, conf) {
    console.log('==================== BAR PLOT =======================');
    conf = normalize_conf(d3data, conf);

    // THIS IS TO ALLOW PLOT TO BE CLICAKBLE and SEND USER to a TABLE VIEW OF THE REGION CLICKED
    // // retrieve the GET query from the URI of this page:
    // conf.query = query2obj();
    // // Change the query to request a table view instead of the plot view that got us to this page/plot
    // delete conf.query.plot;
    // conf.query.table = "fast";

    // TODO: standardize on the "series" data structure below which is also used in the line-plot
    var layers = split_d3_series(d3data);
    for (var i=0; i<layers.length; i++) {
        for (var j=0; j<layers[i].length; j++) {
            layers[i][j].series = layers[i];
            layers[i][j].layer  = layers[i];
            layers[i][j].col = i;
            layers[i][j].row = j;
            layers[i][j].heading = conf.ylabels[i];
        }
    }
    console.log('layers (d3data as arrays of objects with x,y properties)');
    console.log(layers);

    //d3data = arrays_as_objects(d3data);
    var num_stacks = d3data.length; // number of samples per layer

    conf.xscale = d3.scale.ordinal()
        .domain(d3data.map(function(d) { return d[conf.xfield]; }))
        .rangeRoundBands([0, conf.width], 0.1);
    conf.xlabel = "Horizontal Value (Time?)";
    conf.yscale = d3.scale.linear().range([conf.height, 0]);
    conf.ylabel = "Vertical Value";

    d3data.sort(function(a, b) { return a.x - b.x; });

    var color = d3.scale.linear()
        .domain([0, conf.num_layers - 1])
        .range(["#aad", "#556"]);

    console.log('all_series');
    var all_series = ylabels.map(function(name) {
      var series = { name: name, values: null };
      series.values = d3data.map(function(d) {
            return { series: series, x: d[conf.xfield], y: +d[name] };
      }); // d3data.map(function(d) {
      return series;
    });
    console.log(all_series);

    var ymin = d3.min(all_series, function(series) { return d3.min(series.values, function(d) { console.log(d); return d.y; }); });
    var ymax = d3.max(all_series, function(series) { return d3.max(series.values, function(d) { console.log(d); return d.y; }); });

    console.log([ymin, ymax]);

    conf.yGroupMax = ymax;
    conf.yStackMax = d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); });

    // plot starts out stacked
    conf.yscale = d3.scale.linear()
        .domain([0, conf.yStackMax])
        .range([conf.height, 0]);

    // Dependencies:
    //   miner/js/plot-util.js
    //   d3.js

    function mouseover(d) {
        var focus = d3.select("g.focus");
        // var text_anchor = conf.xscale(d.x) > d3.mean(conf.xscale.range()) ? "end" : "start";
        focus.attr("transform", "translate(" + conf.xscale(d.x) + "," + conf.yscale(d3.max([d.y0, d.y])) + ")");
        var tt = d.heading + ": " + (d.y).toFixed(1) + "%";
        var text = focus.select("text").text(tt).node();
        var SVGRect = text.getBBox();
        focus.select("rect").attr("x", SVGRect.x).attr("y", SVGRect.y).attr("width", SVGRect.width).attr("height", SVGRect.height);
        console.log(d);
        console.log(conf.xscale(d.x));
        console.log(d3.mean(conf.xscale.range()));
        console.log("translate(" + conf.xscale(d.x) + "," + conf.yscale(d.y0) + ")");
    }


    function mouseout(d) {
      var focus = d3.select("g.focus");
      focus.select("text").text("");
      focus.select("rect").attr("width", 0).attr("height", 0);
        
      // FIXME: doesn't work
      // selector = ".row-"+d.row + ".col-"+d.col;
      // console.log('mouse out selector: ' + selector);
      // console.log(d);
      // d3.select().classed('hover', false);
    }


    var svg = create_svg_element(conf);

    // don't put a tick mark on bar-plots
    var xAxis = create_xaxis(conf).tickSize(0).tickPadding(6).orient("bottom");

    var yAxis = create_yaxis(conf).ticks(10, "%");

    // var yAxis = d3.svg.axis()
    //     .scale(conf.yscale)
    //     .orient("left");

    // // need something like this here to append the series data to each rect
    // var series = svg.selectAll(".series")
    //     .data(all_series)
    //   .enter().append("g")
    //     .attr("class", "series");


    var layer = svg.selectAll(".layer")
        .data(layers)
      .enter().append("g")
        .attr("class", "layer")
        .style("fill", function(d, i) { return color(i); });

      // chart.selectAll(".bar")
      //     .data(d3data)
      //   .enter().append("rect")
      //     .attr("class", "bar")
      //     .attr("x", function(d) { return x(d.name); })
      //     .attr("y", function(d) { return conf.yscale(d.value); })
      //     .attr("height", function(d) { return conf.height - y(d.value); })
      //     .attr("width", x.rangeBand());
    var rect_element;

    var rect = layer.selectAll("rect")
        .data(function(d) { console.log(d); return d; })
      .enter().append("rect")
        .attr("x", function(d) { return conf.xscale(d[conf.xfield]); })
        .attr("y", conf.height)
        .attr("width", conf.xscale.rangeBand())
        .attr("class", function(d) { return "bar row-" + d.row + " col-" + d.col; })
        .attr("height", 0)
        .on("mouseover", mouseover)
        .on("mouseout", mouseout);
    //    .on("click", mouseclick);

    rect.transition()
        .delay(function(d, i) { return i * 10; })
        .attr("y", function(d) { return conf.yscale(d.y0 + d.y); })
        .attr("height", function(d) { return conf.yscale(d.y0) - conf.yscale(d.y0 + d.y); });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + conf.height + ")")
        .call(xAxis);

    d3.selectAll("input").on("change", change);

    // focus must be the last SVG element so it will be on top
    var focus = svg.append("g").attr("class", "focus");
    var text = focus.append("text").attr("x", 0).attr("y", -12).attr("text-anchor", "start");
    focus = insert_text_background(focus);

    if (typeof conf.stacked == "undefined") {
        var timeout = setTimeout(function() {
          d3.select("input[value=\"grouped\"]").property("checked", true).each(change);
        }, 2000); }
    else {
        d3.select(conf.stacked == true ? "input[value=\"stacked\"]" : "input[value=\"grouped\"]").property("checked", true).each(change);
    }

    function change() {
      clearTimeout(timeout);
      if (this.value === "grouped") { transitionGrouped(); }
      else { transitionStacked(); }
    }

    function transitionGrouped() {
      conf.yscale.domain([0, conf.yGroupMax]);

      rect.transition()
          .duration(500)
          .delay(function(d, i) { return i * 10; })
          .attr("x", function(d, i, j) { return conf.xscale(d[conf.xfield]) + conf.xscale.rangeBand() / conf.num_layers * j; })
          .attr("width", conf.xscale.rangeBand() / conf.num_layers)
        .transition()
          .attr("y", function(d) { return conf.yscale(d.y); })
          .attr("height", function(d) { return conf.height - conf.yscale(d.y); });
      conf.stacked = false;
      mouseover.conf = conf;
      mouseout.conf = conf;
    }

    function transitionStacked() {
      conf.yscale.domain([0, conf.yStackMax]);

      rect.transition()
          .duration(500)
          .delay(function(d, i) { return i * 10; })
          .attr("y", function(d) { return conf.yscale(d.y0 + d.y); })
          .attr("height", function(d) { return conf.yscale(d.y0) - conf.yscale(d.y0 + d.y); })
        .transition()
          .attr("x", function(d) { return conf.xscale(d[xfield]); })
          .attr("width", conf.xscale.rangeBand());
      conf.stacked = true;
      mouseover.conf = conf;
      mouseout.conf = conf;
    }

} // function bar_plot(d3data)
