import moment from "moment";
export function fullVizFormatter(params) {
  let mmt = moment;
  mmt.locale("zh-cn");
  mmt.defaultFormat = "L";
  let template = "";
  switch (params.dataType) {
    case "edge": {
      if (["ParentOf", "ChildOf"].includes(params.data.category)) {
        // console.log(params);
        return `
<div style="max-width: 400px;white-space:pre-wrap;overflow-wrap: break-word;hyphens: auto;"><h3 style="margin-bottom: 5px">关系类型：${params.data.category}</h3><span>关系名称：${params.data.name}</span>
<span>源结点：${params.data.source}</span>
<span>宿结点：${params.data.target}</span>
</div>
`;
      } else if (["Affects", "Has"].includes(params.data.category)) {
        // console.log(params);
        return `
<div style="max-width: 400px;white-space:pre-wrap;overflow-wrap: break-word;hyphens: auto;"><h3 style="margin-bottom: 5px">关系类型：${params.data.category}</h3><span>关系名称：${params.data.name}</span>
<span>源结点：${params.data.source}</span>
<span>宿结点：${params.data.target}</span>
<span>受影响资产：${params.data.assets}</span>
</div>
      `;
      }
      return template;
    }
    case "node": {
      switch (params.data.category) {
        case 0: {
          let props = JSON.parse(params.data.props);
          return `
<div style="max-width: 400px;white-space:pre-wrap;overflow-wrap: break-word;hyphens: auto;"><h3 style="margin-bottom: 5px">漏洞名称：${
            params.data.name
          }</h3><span>标签：${params.data.type}</span>
<span>数据更新日期：${mmt(params.data.timestamp).format()}</span>
<span>漏洞更新日期：${mmt(props.vuln.last_update_date).format()}</span>
<span>漏洞发布日期：${mmt(props.vuln.publish_date).format()}</span>
<span>描述：${props.vuln.desc}</span>
</div>
`;
        }
        case 1: {
          return `
            <div style="max-width: 400px;white-space:pre-wrap;overflow-wrap: break-word;hyphens: auto;"><h3 style="margin-bottom: 5px">资产家族名称：${params.data.name}</h3><span>标签：${params.data.type}</span>
            </div>
        `;
        }
        case 2:
        case 3:
        case 4:
        case 5: {
          // asset
          let props = JSON.parse(params.data.props);
          return `
<div style="max-width: 400px;white-space:pre-wrap;overflow-wrap: break-word;hyphens: auto;"><h3 style="margin-bottom: 5px">资产名称：${
            props.title
          }</h3><span>标签：${params.data.type}</span>
<span>资产标识：${props.cpe23uri}</span>
<span>数据更新日期：${mmt(props.timestamp).format()}</span>
</div>
        `;
        }
        case 6:
          break;
      }
      return template;
    }
  }
}

export function kgStatsFormatter(params) {
  let template = `
<div style="max-width: 400px;white-space:pre-wrap;overflow-wrap: break-word;hyphens: auto;"><h3 style="margin-bottom: 5px">类型：${
    params.data.name
  }</h3><span>数量：${params.data.value}</span>
<span>占比：${params.data.percentage.toLocaleString(undefined, {
    style: "percent",
    minimumFractionDigits: 2,
  })}</span>
</div>
  `;
  return template;
}
