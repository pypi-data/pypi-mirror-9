function Graph(target) {
    var obj = {

        width: 700,
        height: 700,
        target_el: null,
        data_url: null,
        force: null,
        svg: null,
        link: [],
        node: [],
        center_index: null,
        anonymous: false,


        init: function(target) {
            this.target_el = d3.select(target),
            this.force = d3.layout.force()
                .linkDistance(70)
                //.linkStrength(function(d) { console.log(d.siblings); return d.siblings ? 1 / d.siblings : 1; })
                .charge(function(d) { return d.id === 1 ? -1500 : -600; })
                //.chargeDistance(300)
                .gravity(0.08)
                .friction(0.8)
                .on("tick", this.tick.bind(this));
        },


        load: function(dataurl) {
            var self = this,
                topsvg,
                zoom;

            if (!this.data_url) { this.data_url = dataurl; }
            this.target_el.selectAll("svg").remove();
            zoom = d3.behavior.zoom().on("zoom", this.rescale.bind(this));
            topsvg = this.target_el.append("svg:svg")
                .attr("width", "100%")
                .attr("height", "100%")
                .call(zoom)
                .on("dblclick.zoom", function() {
                    zoom.translate([0,0]).scale(1).event(d3.select(this));
                });
            this.svg = topsvg.append("svg:g")
                .attr("width", "100%")
                .attr("height", "100%")

            this.link = this.svg.selectAll(".link");
            this.node = this.svg.selectAll(".node");

            d3.json(dataurl, function(error, json) {
                self.force
                    .nodes(json.nodes)
                    .links(json.links);
                self.center_index = json.center;
                self.anonymous = json.anonymous;
                self.redraw();
            });
        },



        redraw: function() {
            var self = this;

            // Compute the width
            this.width = this.target_el.property("offsetWidth") - 2; // border
            this.height = this.target_el.property("offsetHeight");
            this.force.size([this.width, this.height]);

            // Compute node placement
            if (this.center_index !== null) {
                var center_node = this.force.nodes()[this.center_index];
                center_node.x = this.width / 2;
                center_node.y = this.height / 2;
            }
            var nodes = this.force.nodes(),
                first_circle = [],
                distance_step = 100,
                slice_angle;
            for (var i=0; i < nodes.length; i++) {
                if (nodes[i].circle === 1) { first_circle.push(nodes[i]); }
            }
            if (first_circle.length) { // 0 if no center is set
                slice_angle = 2 * Math.PI / first_circle.length
                function set_coords(node, branchid, randomize) {
                    node.x = Math.cos(branchid * slice_angle) * distance_step * node.circle + self.width / 2;
                    node.y = Math.sin(branchid * slice_angle) * distance_step * node.circle + self.height / 2;
                    if (randomize) {
                        node.x += Math.random() * 100 - 50;
                        node.y += Math.random() * 100 - 50;
                    }
                    if (node.x < 0) { node.x = 0; }
                    if (node.x > self.width) { node.x = self.width; }
                    if (node.y < 0) { node.y = 0; }
                    if (node.y > self.height) { node.x = self.height; }
                }
                for (var i=0 ; i < first_circle.length; i++) {
                    set_coords(first_circle[i], i, false);
                    for (var j=0; j<nodes.length; j++) {
                        if (nodes[j].circle < 2) { continue; }
                        if (nodes[j].branch === first_circle[i].name) {
                            set_coords(nodes[j], i, true);
                        }
                    }
                }
            }

            // (Re)start the force layout.
            this.force.start();

            // Update links.
            this.link = this.link.data(this.force.links(),
                function(d) { return d.source.id+"|"+d.target.id+"|"+d.css; });
            this.link.exit().remove();
            this.link.enter().insert("path", ".node")
                .attr("class", function(d) {
                    var css = "link";
                    if (d.css) { css += " " + d.css; }
                    if (d.dotted) { css += " dotted"; }
                    return css;
                 });

            // Update nodes.
            this.node = this.node.data(this.force.nodes(), function(d) { return d.id; });
            this.node.exit().remove();
            var nodeEnter = this.node.enter().append("g")
                .attr("class", function(d) {
                    var cls = "node";
                    if (typeof d.circle !== 'undefined') {
                        cls += " circle-" + d.circle;
                    }
                    return cls;
                });
            // circle
            nodeEnter.append("circle")
                .attr("r", function(d) { return d.size || 10; });
            // text
            nodeEnter.append("text")
                .attr("dy", ".35em")
                .text(function(d) { return d.name; })
                .attr("class", function(d, i) {
                    if (typeof d.circle !== 'undefined' && d.circle < 2) {
                        return "";
                    } else {
                        return "full";
                    }
                });
            // abbrev
            nodeEnter.each(function(d, i) {
                if (typeof d.circle !== 'undefined' && d.circle < 2) { return; }
                d3.select(this).append("text")
                    .attr("dy", ".35em")
                    .text(function(d) { return d.name.charAt(0); })
                    .attr("class", "abbrev");
            });
            // text background
            nodeEnter.each(function(d, i) {
                //var bbox = this.getElementsByTagName("text")[0].getBBox();
                var rect = d3.select(this).insert("rect", "circle"),
                    bbox;
                if (typeof d.circle !== 'undefined' && d.circle < 2) {
                    bbox = this.getElementsByTagName("text")[0].getBBox();
                    rect.attr("x", bbox.x)
                        .attr("y", bbox.y)
                        .attr("width", bbox.width)
                        .attr("height", bbox.height);
                }
            });
            // node is draggable except if fixed
            nodeEnter.filter(function(d) { return (! d.fixed); })
                .call(this.force.drag)
                .on("mousedown", function() { d3.event.stopPropagation(); });

            // anonymous status
            this.toggleAbbrev(this.anonymous);

            // done!
            this.target_el.select("img.ajaxloader").remove();
        },


        rescale: function() {
            var trans = d3.event.translate,
                scale = d3.event.scale;
            this.svg.attr("transform",
                "translate(" + trans + ")"
                + " scale(" + scale + ")");
        },


        // On each iteration (tick)
        tick: function() {
            this.link.attr("d", function(d) {
                var radius = 0, sweep = 0;
                if (d.siblings > 1) {
                    radius = 200 / (Math.floor(d.sibling_id / 2) + 1);
                    sweep = d.sibling_id % 2;
                }
                return "M"+d.source.x+","+d.source.y+" A"+radius+","+radius+" 0 0,"+sweep+" "+d.target.x+","+d.target.y;
            });
            this.node.attr("transform",
                function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        },


        toggleAbbrev: function(checked) {
            this.node.each(function(d, i) {
                if (typeof d.circle !== 'undefined' && d.circle < 2 ) return;
                var textfull = d3.select(this.getElementsByTagName("text")[0]),
                    textabbrev = d3.select(this.getElementsByTagName("text")[1]),
                    bg = d3.select(this.getElementsByTagName("rect")[0]),
                    bbox;
                if (checked) {
                    textfull.style("display", "none");
                    textabbrev.style("display", "block");
                    bg.attr("width", 0).attr("height", 0);
                } else {
                    textabbrev.style("display", "none");
                    textfull.style("display", "block");
                    bbox = textfull[0][0].getBBox();
                    bg.attr("x", bbox.x)
                      .attr("y", bbox.y)
                      .attr("width", bbox.width)
                      .attr("height", bbox.height);
                }
            });
        },


        stop: function() {
            this.force.stop();
        }

    };
    obj.init(target);
    return obj;
}


function build_graph(target, dataurl) {
    var graph = Graph(target);
    //window.onresize = graph.redraw;
    graph.load(dataurl);
    return graph;
}
