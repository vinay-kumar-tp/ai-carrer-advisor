/**
 * A dependency-free code editor with syntax highlighting.
 *
 * A transparent <textarea> sits exactly on top of a highlighted <pre>, so the
 * browser handles all editing/caret/selection behaviour while the visible text
 * comes from the tokenizer below. Both layers share identical font metrics and
 * padding, which is what keeps them aligned.
 */
import React, { useLayoutEffect, useMemo, useRef } from 'react';
import type { Language } from '../../pages/codequest/types';

const KEYWORDS: Record<Language, string[]> = {
  python: [
    'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif',
    'else', 'except', 'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
    'lambda', 'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while',
    'with', 'yield', 'self',
  ],
  javascript: [
    'await', 'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default',
    'delete', 'do', 'else', 'export', 'extends', 'false', 'finally', 'for', 'function', 'if',
    'import', 'in', 'instanceof', 'let', 'new', 'null', 'of', 'return', 'super', 'switch', 'this',
    'throw', 'true', 'try', 'typeof', 'undefined', 'var', 'void', 'while', 'yield',
  ],
  cpp: [
    'auto', 'bool', 'break', 'case', 'catch', 'char', 'class', 'const', 'continue', 'default',
    'delete', 'do', 'double', 'else', 'enum', 'false', 'float', 'for', 'goto', 'if', 'include',
    'inline', 'int', 'long', 'namespace', 'new', 'nullptr', 'operator', 'private', 'protected',
    'public', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'template',
    'this', 'throw', 'true', 'try', 'typedef', 'typename', 'union', 'unsigned', 'using', 'virtual',
    'void', 'while',
  ],
  java: [
    'abstract', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue',
    'default', 'do', 'double', 'else', 'enum', 'extends', 'false', 'final', 'finally', 'float',
    'for', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new',
    'null', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'super',
    'switch', 'synchronized', 'this', 'throw', 'throws', 'true', 'try', 'void', 'while',
  ],
};

const LINE_COMMENT: Record<Language, string> = {
  python: '#',
  javascript: '//',
  cpp: '//',
  java: '//',
};

const escapeHtml = (text: string) =>
  text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/**
 * Single-pass tokenizer. Comments and strings are consumed greedily so their
 * contents never get re-highlighted as keywords.
 */
const highlight = (source: string, language: Language): string => {
  const keywords = new Set(KEYWORDS[language]);
  const comment = LINE_COMMENT[language];
  let out = '';
  let index = 0;

  const wrap = (cls: string, text: string) => `<span class="cq-tok-${cls}">${escapeHtml(text)}</span>`;

  while (index < source.length) {
    const rest = source.slice(index);

    // Line comment
    if (rest.startsWith(comment)) {
      const end = source.indexOf('\n', index);
      const stop = end === -1 ? source.length : end;
      out += wrap('com', source.slice(index, stop));
      index = stop;
      continue;
    }

    // Block comment (C-family)
    if (language !== 'python' && rest.startsWith('/*')) {
      const end = source.indexOf('*/', index + 2);
      const stop = end === -1 ? source.length : end + 2;
      out += wrap('com', source.slice(index, stop));
      index = stop;
      continue;
    }

    // Triple-quoted Python string
    if (language === 'python' && (rest.startsWith('"""') || rest.startsWith("'''"))) {
      const quote = rest.slice(0, 3);
      const end = source.indexOf(quote, index + 3);
      const stop = end === -1 ? source.length : end + 3;
      out += wrap('str', source.slice(index, stop));
      index = stop;
      continue;
    }

    // Single or double quoted string, honouring backslash escapes
    const quoteChar = source[index];
    if (quoteChar === '"' || quoteChar === "'" || quoteChar === '`') {
      let cursor = index + 1;
      while (cursor < source.length) {
        if (source[cursor] === '\\') {
          cursor += 2;
          continue;
        }
        if (source[cursor] === quoteChar) {
          cursor += 1;
          break;
        }
        if (source[cursor] === '\n' && quoteChar !== '`') break;
        cursor += 1;
      }
      out += wrap('str', source.slice(index, cursor));
      index = cursor;
      continue;
    }

    // Number
    const numberMatch = /^\d[\d_]*(\.\d+)?([eE][+-]?\d+)?/.exec(rest);
    if (numberMatch) {
      out += wrap('num', numberMatch[0]);
      index += numberMatch[0].length;
      continue;
    }

    // Identifier / keyword / call
    const wordMatch = /^[A-Za-z_$][\w$]*/.exec(rest);
    if (wordMatch) {
      const word = wordMatch[0];
      const after = rest.slice(word.length).trimStart();
      if (keywords.has(word)) out += wrap('key', word);
      else if (after.startsWith('(')) out += wrap('fn', word);
      else out += escapeHtml(word);
      index += word.length;
      continue;
    }

    // Operators and punctuation
    if (/^[+\-*/%=<>!&|^~?:;,.(){}[\]]/.test(rest)) {
      out += wrap('op', rest[0]);
      index += 1;
      continue;
    }

    out += escapeHtml(rest[0]);
    index += 1;
  }

  return out;
};

type Props = {
  value: string;
  language: Language;
  onChange: (value: string) => void;
  onRun?: () => void;
  onSubmit?: () => void;
  readOnly?: boolean;
};

export const CodeEditor: React.FC<Props> = ({
  value,
  language,
  onChange,
  onRun,
  onSubmit,
  readOnly,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const highlightRef = useRef<HTMLPreElement>(null);

  const lineCount = useMemo(() => value.split('\n').length, [value]);
  const html = useMemo(() => highlight(value, language), [value, language]);

  // The textarea is absolutely positioned, so the highlight layer defines the
  // scroll height. Keep the textarea's height in step with it.
  useLayoutEffect(() => {
    const pre = highlightRef.current;
    const textarea = textareaRef.current;
    if (pre && textarea) {
      textarea.style.height = `${Math.max(pre.scrollHeight, 320)}px`;
    }
  }, [html]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const textarea = event.currentTarget;

    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      if (event.shiftKey) onSubmit?.();
      else onRun?.();
      return;
    }

    if (event.key === 'Tab') {
      event.preventDefault();
      const { selectionStart, selectionEnd } = textarea;
      const next = `${value.slice(0, selectionStart)}    ${value.slice(selectionEnd)}`;
      onChange(next);
      requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = selectionStart + 4;
      });
      return;
    }

    if (event.key === 'Enter') {
      // Preserve the current line's indentation, and add a level after a block opener.
      const { selectionStart } = textarea;
      const lineStart = value.lastIndexOf('\n', selectionStart - 1) + 1;
      const currentLine = value.slice(lineStart, selectionStart);
      const indent = /^[ \t]*/.exec(currentLine)?.[0] ?? '';
      const opensBlock = /[:{[(]\s*$/.test(currentLine);
      if (!indent && !opensBlock) return;

      event.preventDefault();
      const addition = `\n${indent}${opensBlock ? '    ' : ''}`;
      const next = `${value.slice(0, selectionStart)}${addition}${value.slice(textarea.selectionEnd)}`;
      onChange(next);
      const caret = selectionStart + addition.length;
      requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = caret;
      });
    }
  };

  return (
    <div className="cq-editor-wrap">
      <div className="cq-editor-scroll">
        <div className="cq-editor-gutter" aria-hidden="true">
          {Array.from({ length: lineCount }, (_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>
        <div className="cq-editor-area">
          <pre className="cq-editor-highlight" aria-hidden="true" ref={highlightRef}>
            {/* A trailing newline keeps the last line visible while typing. */}
            <code dangerouslySetInnerHTML={{ __html: `${html}\n` }} />
          </pre>
          <textarea
            ref={textareaRef}
            className="cq-editor-input"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            readOnly={readOnly}
            aria-label="Code editor"
          />
        </div>
      </div>
    </div>
  );
};
