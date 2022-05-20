export function forceDirectedGraphSelectHandler(params) {
  console.log(params)
  switch (params.fromActionPayload.dataType) {
    case "node":
      onNodeSelected(params);
      break;
    case "edge":
      onEdgeSelected(params);
      break;
  }
}

function onNodeSelected(params) {
  params.fromActionPayload;
}

function onEdgeSelected(params) {
  params.fromActionPayload;
}
