import * as d3 from "d3";

graph = ({
  nodes: Array.from({length:8}, () => ({})),
  links: [
    {source: 1, target: 0},
    {source: 2, target: 0},
    {source: 3, target: 0},
    {source: 4, target: 0},
    {source: 5, target: 0},
    {source: 6, target: 0},
    {source: 7, target: 0},
  ]
})
{
  const svg = d3.create("svg").attr("viewBox", [0, 0, width, height]),
    link = svg
      .selectAll(".link")
      .data(graph.links)
      .join("line"),
    node = svg
      .selectAll(".node")
      .data(graph.nodes)
      .join("g");
  node.append("circle")
    .attr("r", 12)
    .attr("cursor", "move")
    .attr("fill", "#ccc")
    .attr("stroke", "#000")
    .attr("stroke-width", "1.5px");
  node.append("text").attr("dy", 25).text(function(d) {return d.index})

  yield svg.node();

  const simulation = d3
    .forceSimulation()
    .nodes(graph.nodes)
    .force("link", d3.forceLink(graph.links).distance(100))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .stop();
  for (let i = 0, n = Math.ceil(Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay())); i < n; ++i) {
    simulation.tick();
  }
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y)
    .attr("stroke", "#000")
    .attr("stroke-width", "1.5px")
  node
    .attr("transform", function (d) {return "translate(" + d.x + ", " + d.y + ")";});
}
