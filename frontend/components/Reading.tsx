'use client';
import Markdown from 'react-markdown';
import type {Root} from 'mdast';
import {readingText,readableNumber} from '@/lib/display';

export function NumberValue({value,unit='',currency=null,scope}:{value:string|number|null|undefined;unit?:string;currency?:string|null;scope?:string}){
  const exact=value==null?undefined:`原值：${String(value)} ${currency||({'percent':'%','percentage-point':'百分點'}[unit]||'')}${scope?`；${scope}`:''}`;
  return <span title={exact} aria-label={exact?`${readableNumber(value,unit,currency)}；${exact}`:undefined}>{readableNumber(value,unit,currency)}</span>;
}
export function ResearchMarkdown({children,names={}}:{children:string;names?:Record<string,string>}){
  // Change text/inline-code AST nodes only. Link destinations and fenced code remain intact.
  function readable(){return (tree:Root)=>{
    function visit(node:Root|Root['children'][number]|{type:string;value?:string;children?:unknown[]}){
      if(node.type==='code'||node.type==='blockquote')return;
      if((node.type==='text'||node.type==='inlineCode')&&'value' in node&&typeof node.value==='string'){
        node.value=readingText(node.value,names);
        if(node.type==='inlineCode')(node as {type:string}).type='text';
      }
      if('children' in node&&node.children)node.children.forEach(child=>visit(child as Root));
    }
    visit(tree);
  }}
  return <Markdown remarkPlugins={[readable]}>{children}</Markdown>;
}
