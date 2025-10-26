module.exports = function(file, api) {
  const j = api.jscodeshift;
  const root = j(file.source);

  // 找到所有从 'recharts' 导入的组件名
  const rechartsImports = root.find(j.ImportDeclaration, {
    source: { value: 'recharts' }
  });

  if (rechartsImports.size() === 0) {
    return null; // 不改文件
  }

  // 收集组件名
  const comps = new Set();
  rechartsImports.forEach(path => {
    path.node.specifiers.forEach(spec => {
      if (spec.type === 'ImportSpecifier') {
        comps.add(spec.imported.name);
      }
    });
  });

  // 遍历所有 JSX 元素
  root.find(j.JSXOpeningElement)
    .filter(path => {
      const name = path.node.name;
      return (
        name.type === 'JSXIdentifier' &&
        comps.has(name.name)
      );
    })
    .forEach(path => {
      // 看看属性里有没有 isAnimationActive
      const has = path.node.attributes.some(attr =>
        attr.type === 'JSXAttribute' &&
        attr.name.name === 'isAnimationActive'
      );
      if (!has) {
        // 插入新属性
        path.node.attributes.push(
          j.jsxAttribute(
            j.jsxIdentifier('isAnimationActive'),
            j.jsxExpressionContainer(j.booleanLiteral(false))
          )
        );
      }
    });

  return root.toSource({ quote: 'single', trailingComma: true });
};