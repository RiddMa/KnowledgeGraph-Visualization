// import * as d3 from "d3";
//
// graph = ({
//   nodes: Array.from({length:8}, () => ({})),
//   links: [
//     {source: 1, target: 0},
//     {source: 2, target: 0},
//     {source: 3, target: 0},
//     {source: 4, target: 0},
//     {source: 5, target: 0},
//     {source: 6, target: 0},
//     {source: 7, target: 0},
//   ]
// })
// {
//   const svg = d3.create("svg").attr("viewBox", [0, 0, width, height]),
//     link = svg
//       .selectAll(".link")
//       .data(graph.links)
//       .join("line"),
//     node = svg
//       .selectAll(".node")
//       .data(graph.nodes)
//       .join("g");
//   node.append("circle")
//     .attr("r", 12)
//     .attr("cursor", "move")
//     .attr("fill", "#ccc")
//     .attr("stroke", "#000")
//     .attr("stroke-width", "1.5px");
//   node.append("text").attr("dy", 25).text(function(d) {return d.index})
//
//   yield svg.node();
//
//   const simulation = d3
//     .forceSimulation()
//     .nodes(graph.nodes)
//     .force("link", d3.forceLink(graph.links).distance(100))
//     .force("charge", d3.forceManyBody().strength(-400))
//     .force("center", d3.forceCenter(width / 2, height / 2))
//     .stop();
//   for (let i = 0, n = Math.ceil(Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay())); i < n; ++i) {
//     simulation.tick();
//   }
//   link
//     .attr("x1", d => d.source.x)
//     .attr("y1", d => d.source.y)
//     .attr("x2", d => d.target.x)
//     .attr("y2", d => d.target.y)
//     .attr("stroke", "#000")
//     .attr("stroke-width", "1.5px")
//   node
//     .attr("transform", function (d) {return "translate(" + d.x + ", " + d.y + ")";});
// }

// import ForceGraph3D from "3d-force-graph";
import ForceGraph from "force-graph";

// export function drawGraph() {
//   const N = 300;
//   const gData = {
//     nodes: [...Array(N).keys()].map((i) => ({ id: i })),
//     links: [...Array(N).keys()]
//       .filter((id) => id)
//       .map((id) => ({
//         source: id,
//         target: Math.round(Math.random() * (id - 1)),
//       })),
//   };
//
//   // eslint-disable-next-line no-unused-vars
//   const Graph = ForceGraph3D()(document.getElementById("3d-graph")).graphData(
//     gData
//   );
// }

export function draw2DGraph(graphData) {
  let dom = document.getElementById("graph-container");
  let w = dom.offsetWidth;
  let h = dom.offsetHeight;
  let canvas = document.getElementById("2d-graph");
  canvas.style.position = "fixed";
  canvas.style.top = "0px";
  // eslint-disable-next-line no-unused-vars
  const Graph = ForceGraph()(canvas)
    .graphData(graphData)
    .nodeId("id")
    .nodeLabel("name")
    .width(w)
    .height(h)
    .nodeAutoColorBy("type")
    .linkDirectionalArrowLength(4);
  // .linkCanvasObjectMode(() => "after")
  // .linkCanvasObject((link, ctx) => {
  //   const MAX_FONT_SIZE = 4;
  //   const LABEL_NODE_MARGIN = Graph.nodeRelSize() * 1.5;
  //
  //   const start = link.source;
  //   const end = link.target;
  //
  //   // ignore unbound links
  //   if (typeof start !== "object" || typeof end !== "object") return;
  //
  //   // calculate label positioning
  //   const textPos = Object.assign(
  //     ...["x", "y"].map((c) => ({
  //       [c]: start[c] + (end[c] - start[c]) / 2, // calc middle point
  //     }))
  //   );
  //
  //   const relLink = { x: end.x - start.x, y: end.y - start.y };
  //
  //   const maxTextLength =
  //     Math.sqrt(Math.pow(relLink.x, 2) + Math.pow(relLink.y, 2)) -
  //     LABEL_NODE_MARGIN * 2;
  //
  //   let textAngle = Math.atan2(relLink.y, relLink.x);
  //   // maintain label vertical orientation for legibility
  //   if (textAngle > Math.PI / 2) textAngle = -(Math.PI - textAngle);
  //   if (textAngle < -Math.PI / 2) textAngle = -(-Math.PI - textAngle);
  //
  //   const label = `${link.source.id} > ${link.target.id}`;
  //
  //   // estimate fontSize to fit in link length
  //   ctx.font = "1px Sans-Serif";
  //   const fontSize = Math.min(
  //     MAX_FONT_SIZE,
  //     maxTextLength / ctx.measureText(label).width
  //   );
  //   ctx.font = `${fontSize}px Sans-Serif`;
  //   const textWidth = ctx.measureText(label).width;
  //   const bckgDimensions = [textWidth, fontSize].map(
  //     (n) => n + fontSize * 0.2
  //   ); // some padding
  //
  //   // draw text label (with background rect)
  //   ctx.save();
  //   ctx.translate(textPos.x, textPos.y);
  //   ctx.rotate(textAngle);
  //
  //   ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
  //   ctx.fillRect(
  //     -bckgDimensions[0] / 2,
  //     -bckgDimensions[1] / 2,
  //     ...bckgDimensions
  //   );
  //
  //   ctx.textAlign = "center";
  //   ctx.textBaseline = "middle";
  //   ctx.fillStyle = "darkgrey";
  //   ctx.fillText(label, 0, 0);
  //   ctx.restore();
  // });
}
