
var dispatch = d3.dispatch("showpapers");

$( window ).resize(function() {
  console.log("resize window");
  resize();
});

$( "body" ).resize(function() {
  console.log("resize");
  resize();
});

  Array.prototype.unique = function() {
    var unique = [];
    for (var i = 0; i < this.length; i++) {
        if (unique.indexOf(this[i]) == -1) {
            unique.push(this[i]);
        }
    }
    return unique;
  };

  var datag = null;

  function get_data(dataurl){
    $.getJSON( dataurl, function( data ) {
      datag = data;
      display([]); 
      });
  }

  function display(paperID, k){
      var papers = [];
      $.each(k, function(key){
        innerK = k[key];
        papers = papers.concat(datag["index"][innerK]);
      });
      papers = papers.unique();

    var items = [];
    $.each( papers, function( key ) {
      items.push( "" + datag["papers"][papers[key]] );
    });

    $(paperID).empty();
    $( "<div/>", {
    "class": "my-new-list",
    html: items.join( "" )
    }).appendTo( paperID );    
  }


  function set_paperID(paperID){
    dispatch.on("showpapers", function(keys){
      display(paperID, keys);
    });
  }

function graph_authors(elemID, url, width, height){

$("#authors").empty();

var fisheye = d3.fisheye.circular()
      .radius(240)
      .distortion(6);


var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(-80)
    .linkDistance(30)
    .size([width, height]);

var svg = d3.select(elemID)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json(url, function(error, graph) {
  var n = graph.nodes.length;

  force
      .nodes(graph.nodes)
      .links(graph.links);

  var steps = 1000;
  force.start();
  for (var i = steps; i > 0; --i) force.tick();
  force.stop();

  // Center the nodes in the middle.
  var ox = 0, oy = 0;
  graph.nodes.forEach(function(d) { ox += d.x, oy += d.y; });
  ox = ox / n - width / 2, oy = oy / n - height / 2;
  graph.nodes.forEach(function(d) { d.x -= ox, d.y -= oy; });

  var link = svg.selectAll(".link")
      .data(graph.links)
    .enter().append("line")
      .attr("class", "link")
      .attr("pointer-events", "none")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });

  var node = svg.selectAll(".node")
      .data(graph.nodes)
      .enter().append("circle")
      .attr("class", "node")
      .attr("r", 5)
      .style("fill", function(d) { return color(d.group); })
      .attr("pointer-events", "none")
      .call(force.drag);
      
  var texts = svg.selectAll(".text.label")
                .data(graph.nodes)
                .enter().append("text")
                .attr("class", "label")
                .style("fill", "#555")
                .style("font-family", "Helvetica")
                .style("font-size", "1em")
                .attr("text-anchor","middle")
                .attr("pointer-events", "none")
                .attr("fill-opacity", function(d) { if (d.group == 1) {return 1.0; } else {return 0.0; } })
                .text(function(d) {  if (d.group == 1 || d.group == 4) { return d.name; } else { return ""; }  });

  node.append("title")
      .text(function(d) { return d.name; });

  var active = true;

  var redraw = function(){
    node.each(function(d) { d.fisheye = fisheye(d); })
        .attr("cx", function(d) { return d.fisheye.x; })
        .attr("cy", function(d) { return d.fisheye.y; })
        .attr("r", function(d) { return d.fisheye.z * 5; });


    link.attr("x1", function(d) { return d.source.fisheye.x; })
        .attr("y1", function(d) { return d.source.fisheye.y; })
        .attr("x2", function(d) { return d.target.fisheye.x; })
        .attr("y2", function(d) { return d.target.fisheye.y; });

    var keys = [];
    texts.attr("transform", function(d) {
          return "translate(" + (d.fisheye.x) + "," + (d.fisheye.y - 20) + ")"; })
        .style("font-size", function(d) { if (d.group == 1) {return "1em";} else {return "" + (d.fisheye.z * 0.5) + "em";} })
        .attr("fill-opacity", function(d) { if (d.group == 1) { return 1.0; } else { return (0.15 * d.fisheye.z); } })
        .text(function(d) {  
          if (d.group == 1) { return d.name; }; if ( d.fisheye.z >= 4.4) {keys.push(d.name); return d.name;} else { return ""; }  });

    dispatch.showpapers(keys);
  }

  svg.on("mousemove", function() {
    if (active) fisheye.focus(d3.mouse(this));
    redraw();
  });

  svg.on("mouseout", function() {
    if (active) fisheye.focus(-100000, -100000);
    redraw();
  });

  svg.on("click", function() {
    console.log("Click!");
    active = !active;
    redraw();
  });

  redraw();
});

}