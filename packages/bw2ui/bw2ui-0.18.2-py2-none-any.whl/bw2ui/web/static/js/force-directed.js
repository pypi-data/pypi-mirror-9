var force_directed_graph = function (data, color_scale, w, h, min_size, max_size, svg_selector, button_selector) {
  var svg = d3.select(svg_selector).append("svg:svg")
        .attr("width", w)
        .attr("height", h);

  var bounded = function (value, min, max) {
    var fixed = isNaN(value) ? -Infinity : value;
    return Math.min(max, Math.max(fixed, min));
  }

  var force = d3.layout.force()
      .nodes(data.nodes)
      .links(data.edges)
      .size([w, h])
      .linkDistance(function (link) {
        size = Math.abs(link.target.cum) / Math.abs(data.total) * max_size * 4;
        return bounded(size, 25, 100);
      })
      .charge(-200)
      .gravity(0.05)
      .start();

  var link = svg.selectAll(".link")
      .data(data.edges)
      .enter()
    .append("svg:line")
    .attr("stroke", "#ccc")
    .attr("stroke-width", function (d) {
      size = Math.abs(d.target.cum) / Math.abs(data.total) * max_size / 1.5;
      return bounded(size, 2, 40);
    });

  var node = svg.selectAll("circle.node")
      .data(data.nodes)
      .enter()
        .append("svg:circle")
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })
        .attr("r", function (d) {
          var size = Math.sqrt(Math.pow(max_size, 2) * Math.abs(d.cum) / Math.abs(data.total));
          return bounded(size, min_size, max_size);
        })
        .style("fill", function(d) { return color_scale(d.cat); })
      .call(force.drag);

  node.append("svg:title")
     .text(function (d) { return d.name;});

  force.on("tick", function(e) {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  });

  $(button_selector).click(function (e) {
    if ($(button_selector).text() === "Individual weights") {
      $(button_selector).text("Cumulative weights");
      node.transition().attr("r", function (d) {
        var size = Math.sqrt(Math.pow(max_size, 2) * Math.abs(d.ind) / Math.abs(data.total));
        return bounded(size, min_size, max_size);
      });
      link.transition().attr("stroke-width", function (d) {
        size = Math.abs(d.target.ind) / Math.abs(data.total) * max_size / 1.5;
        return bounded(size, 2, 40);
      });
    } else {
      $(button_selector).text("Individual weights");
      node.transition().attr("r", function (d) {
        var size = Math.sqrt(Math.pow(max_size, 2) * Math.abs(d.cum) / Math.abs(data.total));
        return bounded(size, min_size, max_size);
      });
      link.transition().attr("stroke-width", function (d) {
        size = Math.abs(d.target.cum) / Math.abs(data.total) * max_size / 1.5;
        return bounded(size, 2, 40);
      });
    }
  });
};
