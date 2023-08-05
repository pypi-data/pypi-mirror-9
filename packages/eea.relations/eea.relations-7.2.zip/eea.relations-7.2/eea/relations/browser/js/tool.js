if(!window.EEA){
  var EEA = {
    who: 'eea.relations',
    version: '1.0'
  };
}

EEA.RelationsGraph = function(context, options){
  var self = this;
  self.context = context;
  self.settings = {
    dataurl: 'graph.json'
  };

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.RelationsGraph.prototype = {
  initialize: function(){
    var self = this;
    self.width = self.context.width();
    self.height = parseInt(self.context.data('height'), 10) || 600;

    self.activeNode = null;
    self.data = self.context.data('graph');
    if(self.data) {
      return self.reload();
    }

    jQuery.getJSON(self.settings.dataurl, {}, function (data) {
      self.data = data;
      return self.reload();
    });
  },

  reload: function(){
    var self = this;
    self.graph = new Graph();
    self.colors = {};

    var render = function(r, n) {
      var color = self.colors[n.id];
      var label = r.text(0, 0, n.label.replace(/\s/g, '\n'));
      var set = r.set()
        .push(
          r.circle(-0, 0, 40).attr({
            fill: color,
            stroke: color,
            "stroke-width": 2
          }))
        .push(label);
      return set;
    };

    jQuery.each(self.data.nodes, function(idx, node){
      self.colors[node.name] = Raphael.getColor();
      self.graph.addNode(node.name, {label: node.label, render: render});
    });

    jQuery.each(self.data.edges, function(idx, edge){
      var options = {directed: true};
      var label = edge.label.replace(/\\n/g, ", ");
      var color = self.colors[edge.source];

      options.stroke = color;
      if(edge.color){
        options.fill = color;
        label = '* ' + label;
      }

      if(edge.label){
        options.label = label;
        options['label-style'] = {'fill': color};
      }
      self.graph.addEdge(edge.source, edge.destination, options);
    });

    /* layout the graph using the Spring layout implementation */
    var layouter = new Graph.Layout.Spring(self.graph);
    layouter.layout();

    var renderer = new Graph.Renderer.Raphael(self.context.attr('id'), self.graph, self.width, self.height);
    renderer.draw();

    jQuery.each(self.graph.nodes, function(idx, node){
      node.shape.click(function(){
        self.nodeClick(node);
      });
    });
  },

  nodeClick: function (node) {
    var self = this;

    // Skip on dragging
    if(jQuery(node.shape).data('moved')) {
      jQuery(node.shape).removeData('moved');
      if(self.activeNode) {
        self.activeNode.shape.animate({ 'fill-opacity': 0.2 }, 500);
      }
      return;
    }

    if(self.activeNode && self.activeNode.id == node.id){
      return self.unfocusNode(self.activeNode);
    }
    return self.focusNode(node);
  },

  focusNode: function(node){
    var self = this;
    self.unfocusNode(self.activeNode);
    self.activeNode = node;
    node.shape.animate({ 'fill-opacity': 0.2 }, 500);

    var visible = {};
    jQuery.each(self.graph.edges, function(idx, edge){
      var source = edge.source;
      var target = edge.target;

      edge.hide();
      if((source.id == node.id) || (target.id == node.id)) {
        visible[source.id] = true;
        visible[target.id] = true;
        edge.show();
      }
    });

    jQuery.each(self.graph.nodes, function(idx, node){
      if(!visible[node.id]){
        node.hide(true);
      }else{
        node.show(true);
      }
    });
  },

  unfocusNode: function(node){
    var self = this;
    self.activeNode = null;
    if(node){
      node.shape.animate({ 'fill-opacity': 0.6 }, 500);
    }

    jQuery.each(self.graph.nodes, function(idx, n){
      n.show();
    });
  }
};

jQuery.fn.EEARelationsGraph = function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new EEA.RelationsGraph(context, options);
    context.data('EEARelationsGraph', adapter);
  });
};

jQuery(document).ready(function(){
  var items = jQuery('.eea-relations .graph');
  if(!items.length){
    return;
  }

  var baseurl = jQuery('base').attr('href');
  if(!baseurl){
    baseurl = jQuery('body').data('base-url');
  }
  if(baseurl.endsWith("/")){
    baseurl = baseurl.substring(0, baseurl.length - 1);
  }

  var settings = {
    dataurl: baseurl + '/graph.json'
  };
  items.EEARelationsGraph(settings);
});
